import { useUserStore } from '@/store/user';

export function usePermission() {
  const user = useUserStore();

  function hasPermission(code: string | string[]): boolean {
    if (!code) return true;
    const codes = Array.isArray(code) ? code : [code];
    return codes.some((c) => user.hasPermission(c));
  }

  function hasAllPermissions(codes: string[]): boolean {
    return codes.every((c) => user.hasPermission(c));
  }

  function hasRole(role: string | string[]): boolean {
    const roles = Array.isArray(role) ? role : [role];
    return roles.some((r) => user.hasRole(r));
  }

  return { hasPermission, hasAllPermissions, hasRole };
}
