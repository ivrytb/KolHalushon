export default async function handler(req, res) {
    const { endpoint } = req.query;
    const apiUrl = `https://www.kolhalashon.com/api/${endpoint}`;

    try {
        const response = await fetch(apiUrl);
        const data = await response.json();
        
        // הגדרת כותרות שמאפשרות לדף ה-HTML שלך לקרוא את הנתונים
        res.setHeader('Access-Control-Allow-Origin', '*');
        res.status(200).json(data);
    } catch (error) {
        res.status(500).json({ error: 'Failed to fetch data' });
    }
}
