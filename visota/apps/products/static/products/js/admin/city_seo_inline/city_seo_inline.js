export default function (url) {
  const path = window.location.pathname.split("/");
  const changeIndex = path.indexOf("change");
  const entityId = path[changeIndex - 1];
  let citySEOGroup;
  let initFormsCount;
  let select;

  async function handleSelectChange(e) {
    const field =
      e.target.parentElement.parentElement.parentElement.parentElement;
    if (!field.classList.contains("field-city")) {
      return;
    }
    const fieldsetParent = e.target.closest("fieldset");
    const idInput = fieldsetParent.nextElementSibling;
    const hElem = fieldsetParent.querySelector(".field-header input");
    const tElem = fieldsetParent.querySelector(".field-title input");
    const dElem = fieldsetParent.querySelector(".field-description textarea");
    const cElem = fieldsetParent.querySelector(
      ".field-page_description .ck-content"
    );

    if (e.target.value) {
      e.target.disabled = true;
      hElem.disabled = true;
      hElem.style.opacity = 0.5;
      tElem.disabled = true;
      tElem.style.opacity = 0.5;
      dElem.disabled = true;
      dElem.style.opacity = 0.5;
      cElem?.ckeditorInstance.enableReadOnlyMode("read-only-id");

      const res = await fetch(`${url}${entityId}-${e.target.value}/`, {
        cache: "no-store",
      });
      const data = await res.json();

      initFormsCount.value = 1;

      idInput.value = data.id;
      hElem.value = data.header;
      tElem.value = data.title;
      dElem.value = data.description;
      cElem?.ckeditorInstance.setData(data.page_description || "");

      e.target.disabled = false;
      hElem.disabled = false;
      hElem.removeAttribute("style");
      tElem.disabled = false;
      tElem.removeAttribute("style");
      dElem.disabled = false;
      dElem.removeAttribute("style");
      cElem?.ckeditorInstance.disableReadOnlyMode("read-only-id");
    } else {
      initFormsCount.value = 0;
      hElem.value = "";
      tElem.value = "";
      dElem.value = "";
      idInput.removeAttribute("value");
      cElem?.ckeditorInstance.setData("");
    }
  }

  const handleLoad = () => {
    citySEOGroup = document.getElementById("city_seo_set-group");
    citySEOGroup.addEventListener("change", handleSelectChange);
    initFormsCount = citySEOGroup.querySelector(
      "input[name=city_seo_set-INITIAL_FORMS]"
    );
    select = citySEOGroup.querySelector(".field-city select");
    if (select[select.selectedIndex].value) {
      select.dispatchEvent(new Event("change", { bubbles: true }));
    }
  };

  window.addEventListener("load", handleLoad);
}
