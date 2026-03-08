import { serve } from "bun";
import index from "./index.html";

const server = serve({
  routes: {
    // Serve index.html for all unmatched routes.
    "/*": index,

    "/api/hello": {
      async GET(req) {
        return Response.json({
          message: "Hello, world!",
          method: "GET",
        });
      },
      async PUT(req) {
        return Response.json({
          message: "Hello, world!",
          method: "PUT",
        });
      },
    },

    "/api/hello/:name": async req => {
      const name = req.params.name;
      return Response.json({
        message: `Hello, ${name}!`,
      });
    },

    // Dummy review endpoint — returns mock analysis data for any URL
    "/api/review": {
      async POST(req) {
        const body = await req.json().catch(() => ({}));
        const url = (body as { url?: string }).url ?? "unknown";
        return Response.json({
          url,
          score: 78,
          summary: "Dummy analysis complete.",
          strengths: [
            "Clean semantic HTML structure",
            "Responsive layout detected",
            "HTTPS is enabled",
          ],
          issues: [
            "Several images are missing alt text (accessibility)",
            "No meta description tag found",
            "Large JavaScript bundle — consider code splitting",
          ],
        });
      },
    },
  },

  development: process.env.NODE_ENV !== "production" && {
    // Enable browser hot reloading in development
    hmr: true,

    // Echo console logs from the browser to the server
    console: true,
  },
});

console.log(`🚀 Server running at ${server.url}`);
