export default async function handler(req, res) {
    const { endpoint } = req.query;
    // שימוש ב-API המודרני של קול הלשון
    const targetUrl = `https://www.kolhalashon.com/api/${endpoint}`;

    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET');
    res.setHeader('Content-Type', 'application/json');

    try {
        const response = await fetch(targetUrl, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Referer': 'https://www.kolhalashon.com/',
                'Origin': 'https://www.kolhalashon.com',
                'Accept': 'application/json, text/plain, */*'
            }
        });

        if (!response.ok) {
            return res.status(response.status).json({ error: "Kolel Error", status: response.status });
        }

        const data = await response.json();
        return res.status(200).json(data);
    } catch (error) {
        return res.status(500).json({ error: "Proxy Crash", details: error.message });
    }
}
