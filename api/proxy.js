export default async function handler(req, res) {
    // הגדרות CORS
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET');

    const { url } = req.query;

    if (!url) {
        return res.status(400).send('Missing URL');
    }

    try {
        // פיענוח ה-URL למקרה שנטפרי או הדפדפן קידדו אותו פעמיים
        const targetUrl = decodeURIComponent(url);
        
        const response = await fetch(targetUrl, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        });

        if (!response.ok) {
            return res.status(response.status).send(`KHL error: ${response.statusText}`);
        }

        const data = await response.json();
        return res.status(200).json(data);
    } catch (error) {
        console.error('Proxy error:', error);
        return res.status(500).send('Proxy failed to connect to Kol Halashon');
    }
}
