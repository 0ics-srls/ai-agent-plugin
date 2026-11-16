const userId = getUserId();
const rows = db.query("SELECT * FROM users WHERE id = " + userId);
const byTemplate = db.query(`SELECT * FROM users WHERE id = ${userId}`);
