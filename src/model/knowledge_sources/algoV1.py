from __future__ import annotations

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field

from knowledge_sources.abstract_knowledge_source import AbstractKnowledgeSource
from utils.instance import Instance
from utils.solution import Output


@dataclass
class _OrderState:
    id: int
    remaining: Dict[int, int]  # product_id -> remaining qty

    def is_done(self) -> bool:
        return all(qty <= 0 for qty in self.remaining.values())


@dataclass
class _BoxState:
    id: int
    order_id: Optional[int]
    weight: int = 0
    volume: int = 0
    products: Dict[int, int] = field(default_factory=dict)  # product_id -> qty

    def add(self, prod_w: int, prod_v: int, prod_id: int, qty: int) -> None:
        self.weight += prod_w * qty
        self.volume += prod_v * qty
        self.products[prod_id] = self.products.get(prod_id, 0) + qty


class _ShortestPathResolver:
    """Distance resolver using provided all-pairs shortest path matrix."""

    def __init__(self, instance: Instance) -> None:
        self.known: Dict[tuple[int, int], int] = {}
        for p in instance.graph.get("shortest_distances", []):
            a = p["idDeparture"]
            b = p["idArrival"]
            w = p["distance"]
            self.known[(a, b)] = w
            self.known[(b, a)] = w

    def dist(self, a: int, b: int) -> Optional[int]:
        if a == b:
            return 0
        return self.known.get((a, b))


def _products_by_id(instance: Instance) -> Dict[int, dict]:
    return {p["id"]: p for p in instance.products}


def _next_nearest_product(current_loc: int, candidate_products: Set[int], prods_by_id: Dict[int, dict], resolver: _ShortestPathResolver) -> Optional[int]:
    if not candidate_products:
        return None
    best_pid: Optional[int] = None
    best_d: Optional[int] = None
    for pid in candidate_products:
        loc = prods_by_id[pid]["id_loc"]
        d = resolver.dist(current_loc, loc)
        if d is None:
            continue
        if best_d is None or d < best_d:
            best_d = d
            best_pid = pid
    return best_pid


class AlgoV1(AbstractKnowledgeSource):
    """
    Heuristic V1.

    Input: blackboard.instance (Instance) and blackboard.instance_path
    Output: blackboard.output (dict)
    """

    def verify(self):
        # Ensure an instance is available
        if not hasattr(self.blackboard, "instance"):
            print("Blackboard missing 'instance'")
            return False
        if self.blackboard.instance is None:
            print("Blackboard 'instance' is None")
            return False
        # Instance minimal fields
        inst = self.blackboard.instance
        needed_fields = [
            hasattr(inst, "nb_boxes_trolley"),
            hasattr(inst, "capa_box"),
            hasattr(inst, "mixed_orders_allowed"),
            hasattr(inst, "products"),
            hasattr(inst, "orders"),
            hasattr(inst, "graph"),
        ]
        if not all(needed_fields):
            print("Instance missing required fields")
            return False
        g = inst.graph or {}
        if g.get("departing_depot") is None or g.get("arrival_depot") is None:
            print("Graph missing depot info")
            return False
        if not g.get("shortest_distances"):
            print("No shortest distances provided in instance.graph")
            return False
        return True

    def process(self):
        inst: Instance = self.blackboard.instance
        resolver = _ShortestPathResolver(inst)
        prods = _products_by_id(inst)
        start_loc = inst.graph["departing_depot"]
        end_loc = inst.graph["arrival_depot"]
        K = int(inst.nb_boxes_trolley or 6)  # per tour
        capa = inst.capa_box or [10**9, 10**9]
        max_w = capa[0] if len(capa) > 0 else 10**9
        max_v = capa[1] if len(capa) > 1 else 10**9

        # Orders state: remaining quantities
        orders_state: Dict[int, _OrderState] = {}
        for o in inst.orders:
            rem: Dict[int, int] = {}
            for p in o["products"]:
                pid = p["product"]["id"]
                qty = p["quantity"]
                rem[pid] = rem.get(pid, 0) + qty
            orders_state[o["id"]] = _OrderState(id=o["id"], remaining=rem)

        all_order_ids = list(orders_state.keys())

        tours_out: List[dict] = []
        orders_out_map: Dict[int, int] = {}
        tour_id = 1
        global_box_id = 1
        total_travelled_distance = 0
        total_crossed_locations = 0

        while True:
            # Stop condition: all orders done
            if all(orders_state[oid].is_done() for oid in all_order_ids):
                break

            # Activate orders for this tour
            active_orders: List[int] = []
            boxes: List[_BoxState] = []
            if not inst.mixed_orders_allowed:
                # Non-mixte: one order per tour
                for oid in all_order_ids:
                    if not orders_state[oid].is_done():
                        active_orders = [oid]
                        boxes = [_BoxState(id=global_box_id, order_id=oid)]
                        global_box_id += 1
                        break
            else:
                # Mixte: start one box per order up to K
                for oid in all_order_ids:
                    if len(boxes) >= K:
                        break
                    if not orders_state[oid].is_done():
                        active_orders.append(oid)
                        boxes.append(_BoxState(id=global_box_id, order_id=oid))
                        global_box_id += 1

            if not active_orders:
                break

            current_loc = start_loc
            travelled = 0
            crossed_locations = 0

            # Map order -> list of its boxes
            order_to_boxes: Dict[int, List[_BoxState]] = {}
            for b in boxes:
                order_to_boxes.setdefault(b.order_id or -1, []).append(b)

            def can_place_in_any_box(oid: int, prod_id: int, qty_wanted: int) -> int:
                nonlocal global_box_id
                p = prods[prod_id]
                per_w, per_v = p["w"], p["v"]
                placed = 0
                # Try existing boxes
                for b in order_to_boxes.get(oid, []):
                    remain_w = max(0, max_w - b.weight)
                    remain_v = max(0, max_v - b.volume)
                    by_w = (remain_w // max(1, per_w)) if per_w > 0 else qty_wanted
                    by_v = (remain_v // max(1, per_v)) if per_v > 0 else qty_wanted
                    can_add = min(qty_wanted - placed, by_w, by_v)
                    if can_add > 0:
                        b.add(per_w, per_v, prod_id, can_add)
                        placed += can_add
                    if placed >= qty_wanted:
                        return placed
                # Open new boxes if needed, limited by trolley capacity K only
                while placed < qty_wanted and len(boxes) < K:
                    new_b = _BoxState(id=global_box_id, order_id=oid)
                    global_box_id += 1
                    boxes.append(new_b)
                    order_to_boxes.setdefault(oid, []).append(new_b)
                    remain_w = max_w
                    remain_v = max_v
                    by_w = (remain_w // max(1, per_w)) if per_w > 0 else qty_wanted
                    by_v = (remain_v // max(1, per_v)) if per_v > 0 else qty_wanted
                    can_add = min(qty_wanted - placed, by_w, by_v)
                    if can_add <= 0:
                        break
                    new_b.add(per_w, per_v, prod_id, can_add)
                    placed += can_add
                return placed

            def can_placeable_units(oid: int, prod_id: int) -> int:
                p = prods[prod_id]
                per_w, per_v = p["w"], p["v"]
                total = 0
                for b in order_to_boxes.get(oid, []):
                    remain_w = max(0, max_w - b.weight)
                    remain_v = max(0, max_v - b.volume)
                    by_w = (remain_w // max(1, per_w)) if per_w > 0 else 10**9
                    by_v = (remain_v // max(1, per_v)) if per_v > 0 else 10**9
                    total += max(0, min(by_w, by_v))
                available_slots = max(0, K - len(boxes))
                if available_slots > 0:
                    by_w = (max_w // max(1, per_w)) if per_w > 0 else 10**9
                    by_v = (max_v // max(1, per_v)) if per_v > 0 else 10**9
                    cap = max(0, min(by_w, by_v))
                    total += available_slots * cap
                return total

            while True:
                # Collect needed products
                needed: Set[int] = set()
                for oid in active_orders:
                    if not orders_state[oid].is_done():
                        for pid, qty in orders_state[oid].remaining.items():
                            if qty > 0:
                                needed.add(pid)
                if not needed:
                    break
                # Filter to placeable products given remaining box capacity and K
                placeable: Set[int] = set()
                for pid in needed:
                    total_placeable = 0
                    for oid in active_orders:
                        qty_need = orders_state[oid].remaining.get(pid, 0)
                        if qty_need > 0:
                            total_placeable += min(qty_need, can_placeable_units(oid, pid))
                    if total_placeable > 0:
                        placeable.add(pid)
                if not placeable:
                    break
                nxt = _next_nearest_product(current_loc, placeable, prods, resolver)
                if nxt is None:
                    break
                loc = prods[nxt]["id_loc"]
                dstep = resolver.dist(current_loc, loc)
                if dstep is None:
                    break
                travelled += dstep
                current_loc = loc
                crossed_locations += 1
                # Fill for each active order
                progress = 0
                for oid in active_orders:
                    qty_need = orders_state[oid].remaining.get(nxt, 0)
                    if qty_need <= 0:
                        continue
                    placed = can_place_in_any_box(oid, nxt, qty_need)
                    if placed > 0:
                        orders_state[oid].remaining[nxt] -= placed
                        progress += placed
                if progress == 0:
                    break

            # Return to arrival depot
            if current_loc is not None and end_loc is not None:
                dend = resolver.dist(current_loc, end_loc)
                if dend is not None:
                    travelled += dend
                    crossed_locations += 1

            # Materialize boxes for this tour
            boxes_out: List[dict] = []
            for b in boxes:
                if not b.products:
                    continue
                bps = [{"product_id": pid, "quantity": qty} for pid, qty in b.products.items()]
                boxes_out.append({
                    "id": b.id,
                    "order_id": b.order_id or -1,
                    "weight": b.weight,
                    "volume": b.volume,
                    "boxe_products": bps,
                })

            if boxes_out:
                # Update per-order box counts
                per_order_new: Dict[int, int] = {}
                for b in boxes_out:
                    oid = b["order_id"]
                    per_order_new[oid] = per_order_new.get(oid, 0) + 1
                for oid, cnt in per_order_new.items():
                    orders_out_map[oid] = orders_out_map.get(oid, 0) + cnt

                tours_out.append({"id": tour_id, "boxes": boxes_out})
                tour_id += 1
                total_travelled_distance += travelled
                total_crossed_locations += crossed_locations

        # Compute stats
        all_boxes = [b for t in tours_out for b in t["boxes"]]
        if all_boxes:
            avg_weight = int(round(sum(b["weight"] for b in all_boxes) * 100 / (len(all_boxes) * max(1, max_w))))
            avg_volume = int(round(sum(b["volume"] for b in all_boxes) * 100 / (len(all_boxes) * max(1, max_v))))
        else:
            avg_weight = 0
            avg_volume = 0

        orders_out = [{"id": oid, "nbr_boxes": orders_out_map.get(oid, 0)} for oid in sorted(orders_out_map)]

        output = Output(
            filename=getattr(self.blackboard, "instance_path", "instance.txt"),
            travelled_distance=total_travelled_distance,
            crossed_locations=total_crossed_locations,
            avg_weight=avg_weight,
            avg_volume=avg_volume,
            tours=tours_out,
            orders=orders_out,
        )

        self.blackboard.output = output

        return self.blackboard