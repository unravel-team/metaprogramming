export default async function Home() {
  const heading = await Promise.resolve("TypeScript Scaffold");

  return (
    <main>
      <h1>{heading}</h1>
      <p>Next.js App Router application and separately published library.</p>
    </main>
  );
}
