// BUDGET MANAGER PAGE

const guestlistTableBody = document.querySelector('#guestlistTable tbody');


window.addEventListener('load', () => {
   getAllGuests();
});


async function getAllGuests() {
   url = `${LOCALHOST}/U/guestlist/`;

   let handleResponse = async function (response) {
      let guests = await response.json();
      console.log(guests);
      renderGuests(guests);
   }
   fetchRequest(handleResponse, url, 'GET');
}


async function getExpensesInCategory(category_id) {
   url = `${LOCALHOST}/U/budget-manager/expenses-in-category/${category_id}`;

   let handleResponse = async function (response) {
      let guests = await response.json();
      renderGuests(guests);
   }
   fetchRequest(handleResponse, url, 'GET');
}


function renderGuests(guests) {
   guestlistTableBody.innerHTML = '';

   guests.forEach(guest => {

      // let jsonGuest = JSON.stringify(guest);
      let tableRow = `
         <tr class="guestlist-item">
            <td>
               <div class="name">${guest.name}</div>
               <div class="contact d-flex">
                  <a href="tel:${guest.phone_number}"><i class="fas fa-phone-alt fs-5"></i> Call</a>
                  <a href="mailto:${guest.email}" class="ms-3"><i class="fas fa-envelope fs-5"></i> Email</a>
               </div>
            </td>
            <td>${guest.rsvp}</td>
            <td>${guest.note}</td>
            <td>
               <div class="dropdown">
                  <button class="btn btn-secondary btn-sm dropdown-toggle" type="button" id="dropdownMenu2" data-bs-toggle="dropdown" aria-expanded="false"></button>
                  
                  <ul class="dropdown-menu dropdown-menu-end shadow" aria-labelledby="dropdownMenu2">
                     <li><a href="${LOCALHOST}/U/guestlist/${guest.id}/update/" class="dropdown-item" type="button">
                           <i class="fas fa-pen"></i>
                           <span class="ms-3">Edit</span>
                        </a></li>
                     <li onclick="deleteGuest(${guest.id})"><a class="dropdown-item" type="button">
                           <i class="fas fa-trash-alt"></i>
                           <span class="ms-3">Delete</span>
                        </a></li>
                  </ul>
               </div>
            </td>
         </tr>
         `;
      guestlistTableBody.innerHTML += tableRow;
   });
}


// add guest
async function addGuest(event) {
   event.preventDefault();

   let addGuestForm = event.target;
   let formData = new FormData(addGuestForm);
   let url = `${LOCALHOST}/U/guestlist/add-guest/`;
   createUpdateGuestHelper(url, formData);
}


// update guest data
async function updateGuest(event) {
   event.preventDefault();

   let updateGuestForm = event.target;
   let formData = new FormData(updateGuestForm);
   let guestId = updateGuestForm.getAttribute('data-budget-item-id');
   let url = `${LOCALHOST}/U/guestlist/${guestId}/update/`;
   createUpdateGuestHelper(url, formData);
}


async function createUpdateGuestHelper(url, formData) {
   let guestName = formData.get('name');
   let guestEmail = formData.get('email');
   let guestPhoneNumber = formData.get('phone_number');
   let guestRsvp = formData.get('rsvp');
   let guestNote = formData.get('note');

   let guest = {
      name: guestName,
      email: guestEmail,
      phone_number: guestPhoneNumber,
      rsvp: guestRsvp,
      note: guestNote,
   };

   console.log('Submitted guest data:');
   console.log(guest);

   let handleResponse = async function (response) {
      await response.json()
         .then(res => console.log(res.msg));
      // emptyFilter();
      getAllGuests();
   }
   fetchRequest(handleResponse, url, 'POST', JSON.stringify(guest));
}


// delete guest
async function deleteGuest(guestId) {
   let url = `${LOCALHOST}/U/guestlist/${guestId}/delete/`;

   let handleResponse = async function (response) {
      await response.json()
         .then(res => console.log(res.msg));
      getAllGuests();
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