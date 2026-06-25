import client from "./client";

export const getDepartments = () =>
  client.get("/departments/").then((r) => r.data);

export const getMyDeptMembers = () =>
  client.get("/departments/my-dept/members").then((r) => r.data);
