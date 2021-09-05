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

  let id_to_children = null;
  let id_to_parents = {};

  function get_recursive(target, source, encountered) {
    if (encountered.includes(target))
        return [];
    encountered.push(target)
    return source[target].flatMap(child => [child, ...get_recursive(child, source, encountered)])
  }

  function re_flow_possible_playlists() {
    const selected_playlists = $("#id_playlists input:checked").map(function() {return parseInt(this.value)}).get()
    const disabled_playlists = [];
    selected_playlists.forEach(playlist_id => {
      disabled_playlists.push(...get_recursive(playlist_id, id_to_children, []), ...get_recursive(playlist_id, id_to_parents, []))
    })
    playlists = document.querySelectorAll("#id_playlists input")
    playlists.forEach(playlist => {
      const id = parseInt(playlist.value)
      playlist.disabled = disabled_playlists.includes(id) && !selected_playlists.includes(id)
    })
  }


  $(window).ready(() => {
    $.get("/api/playlist_tree", (response) => {
      id_to_children = {}
      Object.entries(response).map(([id_str, {children}]) => {
        id_to_children[parseInt(id_str)] = children
      })
      Object.keys(id_to_children).forEach(id => {
        id_to_parents[id] = [];
      })
      Object.entries(id_to_children).forEach(([parent_id_str, children_ids]) => {
        const parent_id = parseInt(parent_id_str)
        console.log(children_ids)
        children_ids.forEach(child_id => {
          id_to_parents[child_id].push(parent_id)
        })
      })
      re_flow_possible_playlists()
    })
  })

  $("#id_type").change(function(event) {
    if (event.target.value == "FRM"){
      frm_selected()
    } else {
      frm_deselected()
    }
  });

  $("input[name='playlists']").change(function (event) {
    re_flow_possible_playlists()
  })
});
