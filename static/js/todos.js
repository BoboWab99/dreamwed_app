// TODOS PAGE

window.addEventListener('load', () => {
   const dateFilterSelect = document.getElementById('filter-due-date');
   const dateFilter = getDateFilter();

   // Populate Date Filter Options
   for (var key in dateFilter) {
      var dateFilterOption = document.createElement('option');
      dateFilterOption.value = key;
      dateFilterOption.innerHTML = camelCaseToNormalText(key);
      dateFilterSelect.appendChild(dateFilterOption);
   }

   // Handle Check/Uncheck Todo Status Checkbox
   document.querySelectorAll('.change_task_complete').forEach(checkbox => {
      if (checkbox.value == 'False') {
         checkbox.checked = false;
      } else {
         checkbox.checked = true;
      }
   });
});

// JQUERY FILTER FOR TODOS
$(document).ready(function () {
   $('.filter-todos').on('change', function () {
      var categoryFilter = $('.filter-category').children("option:selected").text().toLowerCase();
      var dateFilter = $('.filter-date').children("option:selected").val();
      var noFilter = '---------';

      $('.checklist-item').each(function () {
         var todoCategory = $(this).find('.task-label').text().toLowerCase();
         var todoDueDate = $(this).find('.todo-due-date').text(); // dd/mm/yyyy

         var dateValues = todoDueDate.split('/');
         var dd = Number(dateValues[0]);
         var mm = Number(dateValues[1] - 1);
         var yyyy = Number(dateValues[2]);

         var jsDate = new Date(yyyy, mm, dd);
         jsDate.setHours(0, 0, 0, 0);

         // Show/Hide Todos
         if (categoryFilter == noFilter && dateFilter == noFilter) {
            $(this).show();
         } else if (categoryFilter == noFilter || dateFilter == noFilter) {
            $(this).toggle((todoCategory.includes(categoryFilter) || passesDateFilter(dateFilter, jsDate)));
         } else {
            $(this).toggle((todoCategory.includes(categoryFilter) && passesDateFilter(dateFilter, jsDate)));
         }
      });
   });
});

function fillTaskSavedValues(taskId) {
   var taskContentClass = 'todo_' + taskId + '_content';
   var taskCategoryClass = 'todo_' + taskId + '_category';
   var taskCostClass = 'todo_' + taskId + '_cost';
   var taskDueDateClass = 'todo_' + taskId + '_date';

   var taskContent = document.getElementById(taskContentClass).value;
   var taskCategory = document.getElementById(taskCategoryClass).value;
   var taskCost = document.getElementById(taskCostClass).value;
   var taskDueDate = document.getElementById(taskDueDateClass).value;

   const updateForm = document.getElementById('updateTaskForm');
   updateForm.querySelector('#id_content').value = taskContent;
   updateForm.querySelector('#id_category').value = taskCategory;
   updateForm.querySelector('#id_cost').value = taskCost;
   updateForm.querySelector('#id_due_date').value = taskDueDate;
}

function updateTask(taskId) {
   actionUrl = taskId + '/update';
   document.forms.updateTaskForm.action = actionUrl;
   fillTaskSavedValues(taskId);
}

function getDateFilter() {
   const today = new Date();
   today.setHours(0, 0, 0, 0);
   const todayWeekDay = (today.getDay() + 6) % 7; // Monday=0, Tuesday=1, ..., Sunday=6

   var thisMonthStart = new Date(today);
   thisMonthStart.setDate(1);

   var thisWeekStart = new Date(today);
   thisWeekStart.setDate(today.getDate() - todayWeekDay);
   var thisWeekEnd = new Date(thisWeekStart);
   thisWeekEnd.setDate(thisWeekStart.getDate() + 6);

   var lastWeekEnd = new Date(thisWeekStart);
   lastWeekEnd.setDate(thisWeekStart.getDate() - 1);
   var lastWeekStart = new Date(thisWeekStart);
   lastWeekStart.setDate(thisWeekStart.getDate() - 7);

   var twoWeeksAgoEnd = new Date(lastWeekStart);
   twoWeeksAgoEnd.setDate(lastWeekStart.getDate() - 1);
   var twoWeeksAgoStart = new Date(lastWeekStart);
   twoWeeksAgoStart.setDate(lastWeekStart.getDate() - 7);

   var lastMonthEnd = new Date(thisMonthStart);
   lastMonthEnd.setDate(thisMonthStart.getDate() - 1);
   var lastMonthStart = new Date(lastMonthEnd);
   lastMonthStart.setDate(1);

   const dateFilter = {
      today: {
         start: today,
         end: today,
      },
      thisWeek: {
         start: thisWeekStart,
         end: thisWeekEnd,
      },
      lastWeek: {
         start: lastWeekStart,
         end: lastWeekEnd,
      },
      twoWeeksAgo: {
         start: twoWeeksAgoStart,
         end: twoWeeksAgoEnd,
      },
      oneMonthAgo: {
         start: lastMonthStart,
         end: lastMonthEnd,
      },
   };

   return dateFilter;
}

function passesDateFilter(filterOption, date) {
   const dateFilter = getDateFilter();

   if (!dateFilter.hasOwnProperty(filterOption)) { return true; }
   return date >= dateFilter[filterOption].start && date <= dateFilter[filterOption].end;
}

function camelCaseToNormalText(ccText) {
   const result = ccText.replace(/([A-Z])/g, " $1").toLowerCase();
   return result.charAt(0).toUpperCase() + result.slice(1); // capitalize first letter
}


// change todo status with async
// async function changeTaskStatus(taskId) {
//    let response = await fetch('')
// }