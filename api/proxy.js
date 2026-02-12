export default async function handler(req, res) {
    // מאפשר לכל אתר (כולל האתר שלך) לגשת ל-API הזה
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET');

    // שליפת ה-URL ששלחנו מהדף הראשי
    const { url } = req.query;

    if (!url) {
        return res.status(400).json({ error: 'Missing URL parameter' });
    }

    try {
        const response = await fetch(url);
        const data = await response.json();
        
        // החזרת הנתונים מהשרת של קול הלשון אליך הביתה
        return res.status(200).json(data);
    } catch (error) {
        return res.status(500).json({ error: 'Failed to fetch data' });
    }
}
