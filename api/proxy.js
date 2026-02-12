export default async function handler(req, res) {
    const { endpoint } = req.query;
    // בניית הכתובת בדיוק כפי שבדקנו בדפדפן
    const targetUrl = `https://www.kolhalashon.com/api/${endpoint}`;

    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Content-Type', 'application/json');

    try {
        const response = await fetch(targetUrl, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0',
                'Accept': 'application/json'
            }
        });

        const data = await response.json();
        return res.status(200).json(data);
    } catch (error) {
        return res.status(500).json({ error: "Failed to fetch", details: error.message });
    }
}
