const path = window.location.pathname.split("/");
const changeIndex = path.indexOf("change");
const isEdit = changeIndex !== -1;
const productId = path[changeIndex - 1];

let productImgGroup;
let uploadedImgs;

const handleImgsChange = (e) => {
  // Удаляем все формы с несохраненными (не привязанными к товару) картинками
  const nodesToRemove = productImgGroup.querySelectorAll(
    ".product-img-new-uploading"
  );
  for (let node of nodesToRemove) {
    const deleteButton = node.querySelector(".inline-deletelink");
    deleteButton.dispatchEvent(new Event("click", { bubbles: true }));
  }

  // Кнопка для добавления формы для одной картинки
  addButton = productImgGroup.querySelector(".add-row").querySelector("a");
  // Получаем все файлы добавленные через форму для массового добавления картинок
  const files = e.target.files;

  for (let file of files) {
    // Для каждого файла добовляем одну форму
    addButton.dispatchEvent(new Event("click", { bubbles: true }));
    // Находим эту форму
    const imgs = productImgGroup.querySelectorAll(".dynamic-img_urls");
    const lastImg = imgs[imgs.length - 1];
    // Помечаем ее, как несохраненную (не привязанную к товару)
    lastImg.classList.add("product-img-new-uploading");

    const input = lastImg.querySelector(".field-img_url").firstElementChild;

    // Привязываем к форме файл и вешаем обработчик
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    input.files = dataTransfer.files;
    input.addEventListener("change", handleOneImgChange);

    // Создаем имидж для превью
    const img = document.createElement("img");
    img.width = 150;
    img.height = 150;
    img.style = "display: block; object-fit: contain";
    input.after(img);

    // Вызываем событие, чтобы инпут принял правильное состояние
    input.dispatchEvent(new Event("change", { bubbles: true }));
  }
};

const handleOneImgChange = (e) => {
  // Присоединяем картинку к превью
  const input = e.target;
  let parent = input.parentElement;
  if (parent.tagName !== "TD") {
    parent = parent.parentElement;
  }
  const img = parent.querySelector("img");
  img.src = URL.createObjectURL(input.files[0]);
};

const handleLoad = () => {
  productImgGroup = document.getElementById("img_urls-group");
  uploadedImgs = productImgGroup.querySelectorAll(".dynamic-img_urls");
  for (let img of uploadedImgs) {
    if (!img.classList.contains("has_original")) {
      // Удаляем несохраненные (не привязанные к товару) формы с картинками
      const deleteButton = img.querySelector(".inline-deletelink");
      deleteButton.dispatchEvent(new Event("click", { bubbles: true }));
      continue;
    }
    // Вешаем обработчик событий на сохраненные (привязанные к товару) формы с картинками
    const input = img.querySelector(".field-img_url input");
    input.addEventListener("change", handleOneImgChange);
  }

  // Вешаем обработчик событий на форму для массового добавления картинок
  const multiUpload = document.querySelector("#mulitple_product_img_upload");
  multiUpload.addEventListener("change", handleImgsChange);
};

window.addEventListener("load", handleLoad);
