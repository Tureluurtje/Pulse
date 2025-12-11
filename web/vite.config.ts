import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";

const PROXY_TARGET = "https://api.pulse.kwako.nl";

export default defineConfig({
    plugins: [react()],
    resolve: {
        extensions: [".js", ".jsx", ".ts", ".tsx", ".json"],
        alias: {
            "@": path.resolve(__dirname, "./src"),
        },
    },
    build: {
        target: "esnext",
        outDir: "build",
    },
    server: {
        port: 3000,
        open: true,
        proxy: {
            "/api": {
                target: PROXY_TARGET,
                changeOrigin: true,
                secure: true,
                rewrite: (path) => path.replace(/^\/api/, ""),
            },
        },
    },
});
