export default async function handler(req, res) {
    const { endpoint } = req.query;
    const targetUrl = `https://www.kolhalashon.com/api/${endpoint}`;

    // הגדרת כותרות כדי שהדפדפן שלך בבית יוכל לקרוא את המידע מורסל
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Content-Type', 'application/json');

    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }

    try {
        const response = await fetch(targetUrl, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json'
            }
        });

        if (!response.ok) throw new Error(`Status: ${response.status}`);
        
        const data = await response.json();
        return res.status(200).json(data);
    } catch (error) {
        console.error("Proxy Error:", error);
        return res.status(500).json({ error: 'שגיאה במשיכת נתונים מקול הלשון', details: error.message });
    }
}
