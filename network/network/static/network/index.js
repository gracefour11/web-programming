function edit_post(id) {
    const post_body = document.querySelector(`#post_body_${id}`);
    post_body.style.display = 'none';

    const edit_post_view = document.querySelector(`#edit_post_body_${id}`);
    edit_post_view.style.display = 'block';

    const edit_form = document.querySelector(`#edit_form_${id}`);
    edit_form.onsubmit = () => {
        fetch(`/edit/${id}`, {
            method: 'POST',
            body: JSON.stringify({
                body: document.querySelector(`#edit_text_${id}`).value
            })
        })
        .then(() => {
            post_body.innerHTML = body
            edit_post_view.style.display = 'none'
            post_body.style.display = 'block'
        })
    }
}

function like_or_unlike(id) {
    like_btn = document.getElementById(`like_btn_${id}`)
    const currState = (like_btn.style.color == "salmon") ? "Liked" : "Unliked"
    console.log("currState: " + currState)
    const nextColor = (currState == "Unliked") ? "salmon" : "white"
    console.log("nextColor: " + nextColor)
    const nextLikeState = (currState == "Liked") ? 'false' : 'true'
    console.log("nextLikeState: " + nextLikeState)
    like_count = document.querySelector(`#like_count_${id}`)

    fetch(`like/${id}`, {
        method: 'POST',
        body: JSON.stringify({
            like: nextLikeState
        })
    })
    .then(response => response.json())
    .then(data => {
        like_btn.style.color = nextColor
        console.log(data)
        like_count.innerHTML = `${data['likes']}`.toString()
        console.log(like_btn.innerHTML)
    })
}
