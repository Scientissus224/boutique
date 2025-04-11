
    const container = document.getElementById("produits-container");

    produits.forEach((produit, index) => {
      const produitElement = document.createElement("div");
      produitElement.classList.add("produit");
      produitElement.style.animationDelay = `${index * 0.1}s`;
      produitElement.innerHTML = `
        <div class="badge-promo">-20%</div>
        <img src="${produit.img}" alt="${produit.nom}">
        <div class="produit-info">
          <h3>${produit.nom}</h3>
          <p><del>25.99€</del> <span class="prix-promo">20.99€</span></p>
          <div class="notes">
            <i class="fas fa-star"></i>
            <i class="fas fa-star"></i>
            <i class="fas fa-star"></i>
            <i class="fas fa-star"></i>
            <i class="far fa-star"></i>
            <span>(4.0)</span>
          </div>
          <p class="stock">En stock</p>
        </div>
        <div class="produit-menu">
          <div class="menu-item" onclick="aimerProduit(this)">
              <i class="fas fa-heart"></i>
          </div>
          <div class="menu-item" onclick="partagerProduit('${produit.nom}')">
              <i class="fas fa-share-alt"></i>
          </div>
          <div class="menu-item" onclick="voirDetails()">
              <i class="fas fa-eye"></i>
          </div>
          <div class="menu-item" onclick="ajouterAuPanier()">
              <i class="fas fa-shopping-cart"></i>
          </div>
        </div>
      `;
      container.appendChild(produitElement);
    });

    function trierParPrix(ordre) {
      const produits = Array.from(container.children);
      produits.sort((a, b) => {
        const prixA = parseFloat(a.querySelector("p").textContent.replace("€", ""));
        const prixB = parseFloat(b.querySelector("p").textContent.replace("€", ""));
        return ordre === "asc" ? prixA - prixB : prixB - prixA;
      });
      container.innerHTML = "";
      produits.forEach(produit => container.appendChild(produit));
    }

    function filtrerProduits() {
      const recherche = document.getElementById("recherche").value.toLowerCase();
      const produits = Array.from(container.children);
      produits.forEach(produit => {
        const nom = produit.querySelector("h3").textContent.toLowerCase();
        produit.style.display = nom.includes(recherche) ? "block" : "none";
      });
    }

    function changerAffichage(mode) {
      const produits = Array.from(container.children);
      produits.forEach(produit => {
        produit.classList.toggle("liste-mode", mode === "liste");
      });
    }
    function chargerPage(page) {
        const produitsParPage = 6;
        const produits = Array.from(container.children);
        produits.forEach((produit, index) => {
          produit.style.display = (index >= (page - 1) * produitsParPage && index < page * produitsParPage) ? "block" : "none";
        });
      }
