const express = require("express");
const cors = require("cors");
const cookieParser = require("cookie-parser");
const https = require("https");

const app = express();
const PORT = 3001;
const API_BASE = "https://api.pulse.kwako.nl";

// CORS configuration
const corsOptions = {
    origin: "http://localhost:3000",
    credentials: true,
    methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allowedHeaders: ["Content-Type", "Authorization"],
};

// Enable CORS for all routes
app.use(cors(corsOptions));

// Handle all preflight requests as middleware
app.use((req, res, next) => {
    if (req.method === "OPTIONS") {
        res.header("Access-Control-Allow-Origin", "http://localhost:3000");
        res.header("Access-Control-Allow-Credentials", "true");
        res.header(
            "Access-Control-Allow-Methods",
            "GET,POST,PUT,DELETE,OPTIONS"
        );
        res.header(
            "Access-Control-Allow-Headers",
            "Content-Type,Authorization"
        );
        return res.status(200).end();
    }
    next();
});

app.use(express.json());
app.use(cookieParser());

// Helper function to make HTTPS requests
function fetchFromAPI(method, path, body = null) {
    return new Promise((resolve, reject) => {
        const url = new URL(`${API_BASE}${path}`);
        const options = {
            hostname: url.hostname,
            port: url.port,
            path: url.pathname + url.search,
            method: method,
            headers: {
                "Content-Type": "application/json",
            },
        };

        const req = https.request(options, (res) => {
            let data = "";
            res.on("data", (chunk) => {
                data += chunk;
            });
            res.on("end", () => {
                try {
                    const parsed = JSON.parse(data);
                    resolve({
                        status: res.statusCode,
                        headers: res.headers,
                        body: parsed,
                    });
                } catch (e) {
                    resolve({
                        status: res.statusCode,
                        headers: res.headers,
                        body: data,
                    });
                }
            });
        });

        req.on("error", (error) => {
            reject(error);
        });

        if (body) {
            req.write(JSON.stringify(body));
        }
        req.end();
    });
}

// Proxy POST /auth/login route
app.post("/auth/login", async (req, res) => {
    try {
        const { email, password } = req.body;

        // Forward the login request to the actual API
        const apiResponse = await fetchFromAPI("POST", "/auth/login", {
            email,
            password,
        });

        if (apiResponse.status !== 200) {
            return res.status(apiResponse.status).json(apiResponse.body);
        }

        const data = apiResponse.body;

        // Set HTTP-only cookies for access_token and refresh_token
        if (data.access_token) {
            res.cookie("access_token", data.access_token, {
                httpOnly: true,
                secure: false,
                sameSite: "lax",
                maxAge: 3600000,
            });
        }

        if (data.refresh_token) {
            res.cookie("refresh_token", data.refresh_token, {
                httpOnly: true,
                secure: false,
                sameSite: "lax",
                maxAge: 7 * 24 * 3600000,
            });
        }

        // Return the token response to the client
        res.json(data);
    } catch (error) {
        console.error("Login error:", error);
        res.status(500).json({ error: "Internal server error" });
    }
});

// Proxy GET /auth/validate route
app.get("/auth/validate", async (req, res) => {
    try {
        const accessToken = req.cookies.access_token;

        if (!accessToken) {
            return res.status(401).json({ active: false });
        }

        // Create custom request with Authorization header
        const url = new URL(`${API_BASE}/auth/validate`);
        const options = {
            hostname: url.hostname,
            port: url.port,
            path: url.pathname + url.search,
            method: "GET",
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
        };

        const validateReq = https.request(options, (validateRes) => {
            let data = "";
            validateRes.on("data", (chunk) => {
                data += chunk;
            });
            validateRes.on("end", () => {
                try {
                    const parsed = JSON.parse(data);
                    res.status(validateRes.statusCode).json(parsed);
                } catch (e) {
                    res.status(validateRes.statusCode).send(data);
                }
            });
        });

        validateReq.on("error", (error) => {
            console.error("Validate error:", error);
            res.status(500).json({ error: "Internal server error" });
        });

        validateReq.end();
    } catch (error) {
        console.error("Validate error:", error);
        res.status(500).json({ error: "Internal server error" });
    }
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
    console.log(`Proxying to API: ${API_BASE}`);
});
