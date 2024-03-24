function like(postId) {
  const likeCount = document.getElementById(`likes-count-${postId}`);
  const likeButton = document.getElementById(`like-button-${postId}`);

  fetch(`/like-post/${postId}`, { method: "POST" })
    .then((res) => res.json())
    .then((data) => {
      likeCount.innerHTML = data["likes"];
      if (data["liked"] === true) {
        likeButton.innerHTML = "<i class='bi bi-hand-thumbs-up-fill'></i>";
      } else {
        likeButton.innerHTML = "<i class='bi bi-hand-thumbs-up'></i>";
      }
    })
    .catch((e) => alert("Could not like post."));
}
