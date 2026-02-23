import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
    console.log("Proxy: Received detection request at /api/detect");
    try {
        const formData = await req.formData();
        console.log("Proxy: Forwarding to backend on port 8000");

        // Explicitly target Port 8000
        const backendResponse = await fetch("http://127.0.0.1:8000/api/detect", {
            method: "POST",
            body: formData,
            // Do not set Content-Type header manually for FormData, fetch does it with boundary
        });

        if (!backendResponse.ok) {
            const errorText = await backendResponse.text();
            console.error("Proxy: Backend error:", backendResponse.status, errorText);
            return NextResponse.json(
                { error: `Backend failed with ${backendResponse.status}`, details: errorText },
                { status: backendResponse.status }
            );
        }

        const data = await backendResponse.json();
        console.log("Proxy: Success, returning data");
        return NextResponse.json(data);
    } catch (error: any) {
        console.error("Proxy error:", error);
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
