// VENDORS & BOOKMARKS PAGES

async function renderVendors(vendors) {
   let grid = document.getElementById('vendors-grid');
   grid.innerHTML = '';

   vendors.forEach(vendor => {
      let vendorCard = `
      <div class="col">
         <div class="card h-100">
            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT2ZstL_2V9eO2cQi61ic9Bc1DsR5y2956eZw&usqp=CAU" class="card-img-top" alt="...">
            <div class="card-body">

               <label class="pointer bookmark d-flex align-items-center justify-content-center">
                  <input type="checkbox" value="${vendor.wedplanner_id}" data-vendor-id="${vendor.user_id}" class="bookmark-vendor d-none" onchange="changeBookmarkStatus(this)">
                  <i class="fas fa-heart"></i>
               </label>

               <div class="fs-6"><strong>${vendor.business_name}</strong></div>
               <div class="rating">
                  <i class="fas fa-star"></i>
                  <i class="fas fa-star"></i>
                  <i class="fas fa-star"></i>
                  <i class="fas fa-star"></i>
                  <i class="fas fa-star"></i>

                  <span class="num">4.9 - </span>
                  <span class="num">15 reviews</span>
               </div>
               <div class="card-subtitle mb-2 text-muted">${vendor.location}, ${vendor.city}</div>
               <div class="d-flex justify-content-between cta mt-3">
                  <a href="${LOCALHOST}/vendors/${vendor.user_id}/details" class="card-link">View more</a>
                  <a href="#" class="card-link">Request pricing</a>
               </div>
            </div>
         </div>
      </div>
      `;
      grid.innerHTML += vendorCard;
   });
}


// change bookmark status controller
async function changeBookmarkStatus(checkbox) {
   let vendorId = checkbox.getAttribute('data-vendor-id');
   if (checkbox.checked) {
      bookmarkVendor(vendorId);
   } else {
      removeBookmark(vendorId);
   }
}


// new bookmark
async function bookmarkVendor(vendorId) {
   url = `${LOCALHOST}/vendors/${vendorId}/bookmark`;

   let handleResponse = async function (response) {
      await response.json()
         .then(res => console.log(res.msg));
      if (typeof getAllVendors === 'function') {
         getAllVendors();
      } else {
         getSavedVendors();
      }
   }
   fetchRequest(handleResponse, url, 'GET');
}


// remove bookmark
async function removeBookmark(vendorId) {
   url = `${LOCALHOST}/vendors/${vendorId}/remove-bookmark`;

   let handleResponse = async function (response) {
      await response.json()
         .then(res => console.log(res.msg));
      if (typeof getAllVendors === 'function') {
         getAllVendors();
      } else {
         getSavedVendors();
      }
   }
   fetchRequest(handleResponse, url, 'DELETE');
}


// Vendor Status: bookmarked or not
function activateBookmarkStatus() {
   document.querySelectorAll('input.bookmark-vendor').forEach(checkbox => {
      if (Number(checkbox.value)) {
         checkbox.checked = true;
         checkbox.parentElement.setAttribute('title', 'Undo save vendor');
      } else {
         checkbox.checked = false;
         checkbox.parentElement.setAttribute('title', 'Save vendor');
      }
   });
}