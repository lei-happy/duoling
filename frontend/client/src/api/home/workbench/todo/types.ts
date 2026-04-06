/** 与后端 TodoTaskOut（snake_case）一致 */
export interface TodoTask {
  id: number;
  tenant_code: string;
  title: string;
  description?: string | null;
  creator_id: number;
  assignee_id?: number | null;
  creator_name?: string | null;
  assignee_name?: string | null;
  due_time?: string | null;
  priority: number;
  status: number;
  completed_time?: string | null;
  create_time?: string | null;
  update_time?: string | null;
}
