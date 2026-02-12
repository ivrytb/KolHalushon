export default async function handler(req, res) {
    const { endpoint } = req.query;
    
    // הכתובת המלאה של קול הלשון
    const targetUrl = `https://www.kolhalashon.com/api/${endpoint}`;

    try {
        const response = await fetch(targetUrl);
        const data = await response.json();

        // מאפשר לדפדפן לקבל את המידע בלי חסימת CORS
        res.setHeader('Access-Control-Allow-Origin', '*');
        res.setHeader('Content-Type', 'application/json');
        
        return res.status(200).json(data);
    } catch (error) {
        return res.status(500).json({ error: 'שגיאה במשיכת נתונים' });
    }
}
