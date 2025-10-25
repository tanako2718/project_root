let add = document.getElementById("addTodo");
console.log("1");
add.addEventListener("click", function() {
    var todoList = document.getElementByClass("todoList");
    var newTodo = document.createElement("li");
    newTodo.textContent = "新しいToDo項目";
    console.log("newTodo");
    todoList.appendChild(newTodo);
});