const formatDate = (date) => 
    `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;

const today = new Date();
const threeDaysAgo = new Date();
threeDaysAgo.setDate(today.getDate() - 3);
const fourDaysLater = new Date();
fourDaysLater.setDate(today.getDate() + 4);

function changeURL(url){
    const iframe = document.querySelector("iframe[title='My Iframe Title']");
if (iframe) {
    let currentSrc = new URL(iframe.src);
    currentSrc.searchParams.append('path', url);
    iframe.src = currentSrc.toString();
} else {
    console.log("Iframe with the specified title not found.");
    window.location.href = url;
}

}