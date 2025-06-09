window.fusionJavaScriptHandler = {
    handle: function(_actionString, _dataString) {
        return JSON.stringify({
            sku: window.SKU || "",
            count: window.COUNT || 0
        });
    }
};

function navigateTo(url) {
    fetch(url.toString()).then(result => {
        result.text().then(txt => {
            let parser = new DOMParser();
            let newTree = parser.parseFromString(txt, "text/html");
            document.body.replaceWith(newTree.querySelector("body"));
            scrollTo(0, 0);
            processTree(document);
        });
    });
}

function processTree(tree) {
    for (let a of tree.querySelectorAll("a")) {
        a.addEventListener("click", (e) => {
            e.preventDefault();
            let url = new URL(a.href);
            if (url.host.includes("gobilda.com")) {
                url.host = "localhost:7776";
                url.protocol = "http:";
            }
            navigateTo(url);
        });
    }

    let submitter = tree.getElementById("form-action-addToCart");
    if (submitter != null) {
        submitter.value = "Add to Design";

        let form = submitter.closest("form");

        for (let btn of form.querySelectorAll("button")) {
            btn.remove();
        }

        let sku = form.closest("div[data-sku]").getAttribute("data-sku");

        let countInput = form.querySelector(".form-input--incrementTotal");

        form.addEventListener("submit", (e) => {
            e.preventDefault();
            e.stopImmediatePropagation();
            navigateTo("/submitted");
            window.SKU = sku;
            window.COUNT = parseInt(countInput.value);
        });
    }

    tree.querySelector(".wishlistMenuContainer")?.remove();
}

document.addEventListener("DOMContentLoaded", () => {
    processTree(document);
});
