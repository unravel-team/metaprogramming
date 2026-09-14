export function GET(): Response {
  return Response.json({ status: "ok" }); // [tag:health-route]
}
