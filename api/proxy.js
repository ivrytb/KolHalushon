export default async function handler(req, res) {
    const { endpoint } = req.query;
    const targetUrl = `https://www.kolhalashon.com/api/${endpoint}`;

    // הגדרת כותרות CORS
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }

    try {
        const response = await fetch(targetUrl, {
            method: 'GET',
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': 'https://www.kolhalashon.com/',
                'Origin': 'https://www.kolhalashon.com'
            }
        });

        if (!response.ok) {
            // אם עדיין יש 403, נחזיר את הסטטוס המדויק
            return res.status(response.status).json({ 
                error: 'חסימה מהשרת המקורי', 
                status: response.status 
            });
        }

        const data = await response.json();
        return res.status(200).json(data);
    } catch (error) {
        return res.status(500).json({ error: 'שגיאה פנימית בשרת', details: error.message });
    }
}
