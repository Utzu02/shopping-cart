# Nume: Tudorescu Ioan Daniel  
**Grupa:** 312CC  
**Anul:** I

## Tema IA1: UPBshop – Shopping-Cart Web App (Flask + SQLite + Tailwind)

Deci ca server de python am folosit **Flask**, ca baza de date **SQLite**, ca template engine **Jinja2** si ca framework de CSS **Tailwind**  
Am folosit Tailwind deoarece am mai lucrat cu el si mi se pare mult mai maleabil decat Boostrap dandu mi libertatea de a modifica design ul continutului exact pe placul meu (in Bootstrap mi se pare mai greu sa obtin asta).

**DB-ul** se numeste `shop.db` si se afla in folderul `/database`. Daca nu exista (sau nu e populat), el este creat/populat automat in `server.py` pe baza json-ului `products.json` (folosit ca si schelete pentru exemple). Am facut 3 scheme de DB: `products`, `order` si `orderitem`. `Orderitem` tine minte in mare parte date despre item (id etc) si am facut un relationship intre `order.items` si `orderitem`.

### Pagini

- **base.html:**
    - Template ul de html in care am inclus header-ul si footer-ul. In header sunt 5 link uri catre paginile principale despre care voi vorbi mai jos. De asemenea in stanga e un text ce poarta locul unui logo (**UPBshop.**) pe care daca apesi de duce pe homepage (ruta `/`) si la cart numarul de iteme care se afla in cart este preluat din backend si se actualizeaza cand apesi pe add item.  
    - In header in functie de pagina pe care esti, link ul din header care te ar fi pe acea pagina este putin mai inchis la culoare.
- **index.html:**
    - Se apeleaza pe ruta `/` si se deschide cu un banner generic pe care daca apesi pe **explore deals** da scroll la id-ul `#products` adica la grid ul de produse, iar daca dai pe **view cart** merge pe ruta `/cart`  
    - Inainte de grid ul de produse am pus 2 sectiuni, una de categorie si una de search. In sectiunea de categorii se preiau automat toate categoriile din backend si sunt puse ca si copii in interiorul dropdown ului. Search este functional, facut in backend  
    - Mai departe, in grid se afla toate produsele. Fiecare are o prezentare generala a lui in care scrie numele lui, cel care a pus produsul, categoria si cate sale-uri are. De asemenea este o iconita de cart pe care daca se apasa item-ul se baga in cart si un link de preview care duce pe ruta `/product/{product_id}` (daca produsul e pus din **SQLProducts** ca autor apare **Admin**)
- **cart.html:**
    - Se apeleaza pe ruta `/cart` si contine toate produsele care se afla in cartul nostru. Am pus optiunea bonus de a seta cantitatea produsului (doua butoane de `-`/`+` care adauga sau sterg produse) si optiunea de a sterge produsul (toate produsele de acelasi tip) din cart. Pe "**proceed to checkout**" se apeleaza `/checkout`
- **checkout.html:**
    - Se apeleaza pe ruta `/checkout` si contine un flex cu 2 elemente puse pe coloana. In prima coloana este un rezumat al comenzii cu numele produselor si cate sunt, iar pe a doua coloana este un form cu detaliile cerute in cerinta temei care treubie completate toate. Mai departe dupa ce se da submit se apeleaza pagina `order_confirm.html` despre care voi vorbi mai jos si se salveaza datele despre order in DB, fiind afisate si in consola.  
    - In functie de cate produse s-au cumparat de anumit tip, la acel produs daca ne intoarcem in homepage si ne uitam la el vedem ca i s-au marit sale-urile (am updatat in DB).
- **contact.html:**
    - Se apeleaza pe ruta `/contact` si contine date despre magazin si un form

#### Pe langa paginile cerute in cerinta temei am facut paginile:

- **order_confirm.html:**  
    se apeleaza tot pe ruta `/checkout` ca si `checkout.html` in momentul in care se completeaza formularul si se da post. In pagina sunt vizualizate detalii despre datele din formular si despre comanda (ce produse am cumparat, cate produse si pretul individual si total al produselor). De asemenea aceste detalii sunt afisate si in consola si sunt salvate in DB
- **product.html:**  
    se apeleaza pe ruta `/product/{product_id}` si afiseaza detalii despre produs (nume, pret, descirere, etc). Singura actiune care poate fi facuta este `add_cart`
- **admin_order.html** (sau **SQLOrder**):  
    se apeleaza pe ruta `/admin/order` si afiseaza toate comenzile salvate in database (detalii despre produse si despre client) cu data, ora, id ul comenzii etc
- **admin_products.html** (sau **SQLProducts**):  
    se apeleaza pe ruta `/admin/products` si afiseaza toate produsele salvate in db (pret, vanzari etc). De asemenea am pus si optiunea de a sterge un produs din DB si a adauga unul nou (poti pune nume, descriere, categorie, pret si se poate incarca si poza)  
    In pagina de contact am adaugat si un form pe care daca il completezi se vor afisa toate detaliile lui in consola.  
    M am gandit sa fac si un sistem de login si register, dar nu mi se parea atat de folositor intrucat era doar de forma si scria in tema ca nu e obligatoriu sa fi logat.

Site-ul este `responsive`, iar pentru header la burger am folosit alpine.js, un fel de jquery.
Toata logica de a adauga un item in cos, de a modifica cantitatea itemelor in pagina de cos, de a filtra dupa categorii si de a cauta produsele este facuta in backend in `server.py` si de asta se da refresh automat cand fac una din actiunile astea. M-am gandit sa folosesc un middleware de js pentru actiunile astea sa nu se mai dea refresh, dar am zis ca nu respect unele lucruri din cerinta.

In `dockerfile` am setat ca `VOLUME` folderul `/database` si ar trebui sa ramana consistent db-ul

Am pus `dockerignore` deoarece dau `COPY . .` si sa nu mi se copieze folderul de `DB` ca dupa sa mi dea `eroare` cand ii pun `VOLUME`