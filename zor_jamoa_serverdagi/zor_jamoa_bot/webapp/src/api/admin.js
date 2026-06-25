import client from "./client";

// Arizalar
export const getApplications  = ()       => client.get("/admin/applications").then(r => r.data);
export const approveUser       = (id)     => client.post(`/admin/applications/${id}/approve`).then(r => r.data);
export const rejectUser        = (id)     => client.post(`/admin/applications/${id}/reject`).then(r => r.data);

// Hodimlar
export const getUsers          = (params) => client.get("/admin/users", { params }).then(r => r.data);
export const addUser           = (body)   => client.post("/admin/users", body).then(r => r.data);
export const updateUser        = (id, b)  => client.patch(`/admin/users/${id}`, b).then(r => r.data);
export const deleteUser        = (id)     => client.delete(`/admin/users/${id}`).then(r => r.data);

// Bo'limlar
export const getAdminDepts     = ()       => client.get("/admin/departments").then(r => r.data);
export const addDepartment     = (name)   => client.post("/admin/departments", { name }).then(r => r.data);
export const editDepartment    = (id, n)  => client.patch(`/admin/departments/${id}`, { name: n }).then(r => r.data);
export const deleteDepartment  = (id)     => client.delete(`/admin/departments/${id}`).then(r => r.data);
export const setDeptHead       = (id, uid)=> client.post(`/admin/departments/${id}/set-head`, { user_id: uid }).then(r => r.data);
export const getDeptMembers    = (id)     => client.get(`/admin/departments/${id}/members`).then(r => r.data);

// Hisobot
export const getReport         = (force)  => client.get("/admin/report", { params: { force } }).then(r => r.data);

// Tarqatish
export const getDistribution   = (dept_id)=> client.get("/admin/distribution", { params: dept_id ? { dept_id } : {} }).then(r => r.data);
export const markTaken         = (order_id)=> client.post(`/admin/distribution/${order_id}/taken`).then(r => r.data);
