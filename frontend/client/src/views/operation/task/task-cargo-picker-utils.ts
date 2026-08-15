/** 手动配载：cargoId 可能是 number / string，统一后再比较 */

export function cargoIdKey(id: unknown): number {
  const n = Number(id);
  return Number.isFinite(n) && n > 0 ? n : 0;
}

export function sameCargoId(a: unknown, b: unknown): boolean {
  const key = cargoIdKey(a);
  return key > 0 && key === cargoIdKey(b);
}

export function pickedQuantityForCargo(
  list: Array<{ waybillCargoId?: unknown; quantity?: number }> | null | undefined,
  cargoId: unknown
): number {
  const id = cargoIdKey(cargoId);
  if (!id) return 0;
  return (list || []).reduce((sum, item) => {
    if (!sameCargoId(item.waybillCargoId, id)) return sum;
    return sum + (Number(item.quantity) || 0);
  }, 0);
}

export function remainingAfterPick(
  remainingQuantity: number,
  pickedQuantity: number
): number {
  return Math.max(0, (Number(remainingQuantity) || 0) - (Number(pickedQuantity) || 0));
}

/** 创建成功后从待选列表扣掉本单已配台数 */
export function applyConsumedToCandidates<
  T extends {
    cargoId: unknown;
    waybillId?: unknown;
    remainingQuantity: number;
    allocatedQuantity?: number;
  }
>(
  candidates: T[],
  picked: Array<{ waybillCargoId?: unknown; quantity?: number }>
): T[] {
  const used = new Map<number, number>();
  for (const item of picked) {
    const id = cargoIdKey(item.waybillCargoId);
    if (!id) continue;
    used.set(id, (used.get(id) || 0) + (Number(item.quantity) || 0));
  }
  if (!used.size) return candidates;

  const next: T[] = [];
  for (const row of candidates) {
    const consumed = used.get(cargoIdKey(row.cargoId)) || 0;
    if (!consumed) {
      next.push(row);
      continue;
    }
    const remain = remainingAfterPick(row.remainingQuantity, consumed);
    if (remain <= 0) continue;
    next.push({
      ...row,
      remainingQuantity: remain,
      allocatedQuantity: (Number(row.allocatedQuantity) || 0) + consumed
    });
  }
  return next;
}
