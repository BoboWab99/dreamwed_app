// BUDGET MANAGER PAGE

const budgetItemsTableBody = document.querySelector('#BudgetItemsTable tbody');


window.addEventListener('load', () => {
   getAllbudgetItems();
});


async function getAllbudgetItems() {
   url = `${LOCALHOST}/U/budget-manager/`;

   let handleResponse = async function (response) {
      let budgetItems = await response.json();
      renderBudgetItems(budgetItems);
   }
   fetchRequest(handleResponse, url, 'GET');
}


async function getExpensesInCategory(category_id) {
   url = `${LOCALHOST}/U/budget-manager/expenses-in-category/${category_id}`;

   let handleResponse = async function (response) {
      let budgetItems = await response.json();
      renderBudgetItems(budgetItems);
   }
   fetchRequest(handleResponse, url, 'GET');
}


function renderBudgetItems(budgetItems) {
   budgetItemsTableBody.innerHTML = '';

   budgetItems.forEach(budgetItem => {

      let jsonBudgetItem = JSON.stringify(budgetItem);
      let tableRow = `
         <tr class="budget-item">
            <td class="pointer" title="Click to update this budget item." data-bs-toggle="modal" data-bs-target="#updateExpense" onclick='fillBudgetItemSavedValues(\`${jsonBudgetItem}\`)'>
               <div class="expense-description">${budgetItem.description}</div>
               <a href="#">ADD NOTE</a>
            </td>
            <td class="expense-cost">KES ${budgetItem.cost}</td>
            <td class="expense-paid">KES ${budgetItem.paid ? budgetItem.paid : 0}</td>
            <td>
               <a class="pointer" onclick="deleteBudgetItem(${budgetItem.id})" title="Delete this budget item">
                  <i class="fas fa-trash-alt"></i>
               </a>
            </td>
         </tr>
         `;
      budgetItemsTableBody.innerHTML += tableRow;
   });
}


// fills update form with selected budget item values
async function fillBudgetItemSavedValues(jsonBudgetItem) {
   let budgetItem = JSON.parse(jsonBudgetItem);
   let updateForm = document.forms.updateBudgetItemForm;

   updateForm.querySelector('#id_description').value = budgetItem.description;
   updateForm.querySelector('#id_expense_category').value = validateOutput(budgetItem.expense_category_id);
   updateForm.querySelector('#id_cost').value = budgetItem.cost;
   updateForm.setAttribute('data-budget-item-id', budgetItem.id)
}


async function createBudgetItem(event) {
   event.preventDefault();

   let createBudgetItemForm = event.target;
   let formData = new FormData(createBudgetItemForm);
   let url = `${LOCALHOST}/U/budget-manager/create-budget-item`;
   createUpdateBudgetItemHelper(url, formData);
}


// update budget item
async function updateBudgetItem(event) {
   event.preventDefault();

   let updateBudgetItemForm = event.target;
   let formData = new FormData(updateBudgetItemForm);
   let budgetItemId = updateBudgetItemForm.getAttribute('data-budget-item-id');
   let url = `${LOCALHOST}/U/budget-manager/${budgetItemId}/update`;
   createUpdateBudgetItemHelper(url, formData);
}


async function createUpdateBudgetItemHelper(url, formData) {
   let budgetItemContent = formData.get('description');
   let budgetItemExpenseCategory = formData.get('expense_category');
   let budgetItemCost = formData.get('cost');

   let budgetItem = {
      description: budgetItemContent,
      expense_category: budgetItemExpenseCategory,
      cost: budgetItemCost,
   };

   let handleResponse = async function (response) {
      await response.json()
         .then(res => console.log(res.msg));
      // emptyFilter();
      getAllbudgetItems();
   }
   fetchRequest(handleResponse, url, 'POST', JSON.stringify(budgetItem));
}


// delete budget item 
async function deleteBudgetItem(budgetItemId) {
   let url = `${LOCALHOST}/U/budget-manager/${budgetItemId}/delete`;

   let handleResponse = async function (response) {
      await response.json()
         .then(res => console.log(res.msg));
      getAllbudgetItems();
   }
   fetchRequest(handleResponse, url, 'DELETE');
}


function passesCostFilter(filter, cost, paid) {
   const fully_paid = 'full';
   const partially_paid = 'partial';
   const not_paid = 'no';

   switch (filter) {
      case not_paid:
         return paid == 0;
      case fully_paid:
         return cost == paid;
      case partially_paid:
         return cost > paid && paid > 0;
      default:
         return true;
   }
}


// JQuery Filter For budget items
$(document).ready(function () {
   $('#rsvp-filter').on('change', function () {
      let costFilter = $(this).children("option:selected").val();

      $('tr.budget-item').each(function () {
         let cost = $(this).find('.expense-cost').text();
         let paid = $(this).find('.expense-paid').text();

         cost = Number(cost.slice(3));
         paid = Number(paid.slice(3));

         // Show/Hide budget items
         $(this).toggle(passesCostFilter(costFilter, cost, paid));
      });
   });
});