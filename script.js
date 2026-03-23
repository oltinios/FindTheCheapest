async function loadItems() {
  const res = await fetch("http://127.0.0.1:5000/items");
  const data = await res.json();

  const menu = document.getElementById("menu");
  menu.innerHTML = ""; // clear previous items

  data.forEach(item => {
    const div = document.createElement("div");
    div.className = "item";

    // Add image, name, price, offers
    div.innerHTML = `
      <img src="${item.image || ''}" 
           alt="${item.name}" 
           style="width:100%; height:150px; object-fit:cover; border-radius:5px; margin-bottom:10px;">
      <h2>${item.name}</h2>
      <p>${item.price}</p>
      <p>${item.offers || ""}</p>
    `;

    menu.appendChild(div);
  });
}

// Load items automatically when window opens
window.onload = loadItems;