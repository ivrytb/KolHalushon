export default async function handler(req, res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET');

    const { url } = req.query;
    if (!url) return res.status(400).send('Missing URL');

    try {
        const targetUrl = decodeURIComponent(url);
        
        const response = await fetch(targetUrl, {
            method: 'GET',
            headers: {
                // אלו ה-Headers שגורמים לשרת לחשוב שזה דפדפן אמיתי
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': 'https://www.kolhalashon.com/',
                'Origin': 'https://www.kolhalashon.com'
            }
        });

        if (!response.ok) {
            return res.status(response.status).send(`KHL responded with ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        return res.status(200).json(data);
    } catch (error) {
        return res.status(500).send('Proxy error: ' + error.message);
    }
}
