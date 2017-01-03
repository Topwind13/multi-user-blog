
// add event listener to show edit comment form when click edit button
$(function(){
    $(".edit-btn").click(function(){
      $("#edit_form_"+ this.id).show();
      $("#comment_content_" + this.id).hide();
  });
});

// add css class to show the lable when the values are exist.
$(function(){
  if ($(".lable").val()) {
    $(".lable").parent().addClass("floating-label-form-group-with-value").removeClass(".floating-label-form-group");
  };
});

// add event listener to show delete conformation box when click delete button
$(function(){
  $(".btn-delete").click(function(event){
    if (!confirm('Are you sure to delete this?\n\nYou cannot retrieve this after click OK')) {
      event.preventDefault();
    }
  });
});
