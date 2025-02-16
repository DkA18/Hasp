const formatDate = (date) => 
    `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;

const today = new Date();
const threeDaysAgo = new Date();
threeDaysAgo.setDate(today.getDate() - 3);
const fourDaysLater = new Date();
fourDaysLater.setDate(today.getDate() + 4);

