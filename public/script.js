const API = "http://localhost:3000";
// const API = "https://stockmarket-8e8r.onrender.com";

// Load stocks
async function loadStocks() {
    const res = await fetch(API + "/stocks");
    const data = await res.json();

    const div = document.getElementById("stocks");
    div.innerHTML = "";

    data.forEach(stock => {
        div.innerHTML += `
        <div class="stock">
            <h3>${stock.name}</h3>
            <p>Price: ₹${stock.price}</p>
            <button onclick="buyStock('${stock.name}', ${stock.price})">
                Buy
            </button>
        </div>
        `;
    });
}

// Portfolio
async function loadPortfolio() {
    const res = await fetch(API + "/portfolio");
    const data = await res.json();

    const div = document.getElementById("portfolio");
    div.innerHTML = "";

    data.forEach(stock => {
        div.innerHTML += `
        <div class="stock">
            <h3>${stock.name}</h3>
            <p>Bought At: ₹${stock.price}</p>
            <button onclick="sellStock('${stock.name}')">
                Sell
            </button>
        </div>
        `;
    });
}

// Buy
async function buyStock(name, price) {
    await fetch(API + "/buy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, price })
    });

    loadPortfolio();
}

// Sell
async function sellStock(name) {
    await fetch(API + "/sell", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name })
    });

    loadPortfolio();
}

// Auto refresh stocks every 5 sec
setInterval(loadStocks, 5000);

loadStocks();
loadPortfolio();
