module.exports = async (req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "*");
  res.setHeader("Access-Control-Expose-Headers", "*");

  if (req.method === "OPTIONS") {
    return res.status(204).end();
  }

  const targetUrl = req.query.url;
  const cookie = req.query.cookie || "";

  if (!targetUrl) {
    return res.status(400).send("Missing url parameter");
  }

  const headers = {
    "User-Agent": "plaYtv/7.1.3 (Linux;Android 13) ExoPlayerLib/2.11.6",
    "Accept": "*/*"
  };
  if (cookie) headers["Cookie"] = cookie;

  try {
    const response = await fetch(targetUrl, {
      method: req.method,
      headers,
      redirect: "follow"
    });

    const finalUrl = response.url || targetUrl;
    const baseDir = finalUrl.substring(0, finalUrl.lastIndexOf("/") + 1);
    const contentType = (response.headers.get("content-type") || "application/octet-stream").toLowerCase();

    res.setHeader("Content-Type", contentType);

    // DASH (.mpd): inject <BaseURL> so Shaka resolves video chunks to the real CDN
    if (finalUrl.toLowerCase().includes(".mpd") || contentType.includes("dash+xml")) {
      let xml = await response.text();
      if (!xml.includes("<BaseURL>")) {
        xml = xml.replace(/(<MPD[^>]*>)/i, `$1\n  <BaseURL>${baseDir}</BaseURL>`);
      }
      return res.status(response.status).send(xml);
    }

    // HLS (.m3u8): rewrite relative paths to absolute URLs
    if (finalUrl.toLowerCase().includes(".m3u8") || contentType.includes("mpegurl")) {
      const m3u8 = await response.text();
      const rewritten = m3u8
        .split("\n")
        .map((line) => {
          const t = line.trim();
          if (!t || t.startsWith("#") || t.startsWith("http://") || t.startsWith("https://")) {
            return line;
          }
          return new URL(t, baseDir).href;
        })
        .join("\n");
      return res.status(response.status).send(rewritten);
    }

    // Binary video/audio segments (.m4s, .ts, etc.)
    const buffer = Buffer.from(await response.arrayBuffer());
    return res.status(response.status).send(buffer);
  } catch (err) {
    return res.status(502).send("Proxy error: " + err.message);
  }
};
