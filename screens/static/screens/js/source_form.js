/* global django */
django.jQuery(function($) {
  function frm_selected(){
    console.log("frm");
    $("#id_file").prop('disabled', true);
    $("#id_url").prop('disabled', false);
  }

  function frm_deselected(){
    console.log("not frm");
    $("#id_file").prop('disabled', false);
    $("#id_url").prop('disabled', true);
  }

  $("#id_type").change(function(event) {
    if (event.target.value == "FRM"){
      frm_selected()
    } else {
      frm_deselected()
    }
  });
});
