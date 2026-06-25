import client from "./client";

export const getMyOrders = () =>
  client.get("/orders/my").then((r) => r.data);

export const createOrder = (meal_type) =>
  client.post("/orders/", { meal_type }).then((r) => r.data);

export const createBulkOrder = (user_ids, meal_type) =>
  client.post("/orders/bulk", { user_ids, meal_type }).then((r) => r.data);
