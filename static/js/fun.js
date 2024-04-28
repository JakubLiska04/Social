const newProfilePic = document.getElementById("new-profile-pic");
const postForm = document.getElementById("post-form");
const profilePicUpload = document.getElementById("profile-pic-upload");
let postId;
let userId;
function toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    const arrowButton = document.querySelector(".arrow-button");
    sidebar.classList.toggle("open");
    arrowButton.classList.toggle("open");
}
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; csrftoken=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}
function OpenChats() {
    const chatwindow = document.getElementById("chats");
    const chatButton = document.querySelector(".chatButton");
    chatwindow.classList.toggle("open");
    chatButton.classList.toggle("open");
}
function togglePostForm() {
    postFormContainer.style.display = postFormContainer.style.display === "none" ? "block" : "none";
}

function toggleProfilePicForm() {
    if (profilepicForm) {
        profilepicForm.style.display = profilepicForm.style.display === "none" ? "block" : "none";
    }
}


document.addEventListener("DOMContentLoaded", function () {
    const postTriggerButton = document.getElementById("post-trigger-button");
    const postFormContainer = document.getElementById("post-form-container");

    postTriggerButton.addEventListener("click", function () {
        togglePostForm();
    });

    if (postForm) {
        postForm.addEventListener("submit", function (event) {
            event.preventDefault();
            const formData = new FormData(postForm);

            fetch(postForm.action, {
                method: "POST",
                body: formData,
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        togglePostForm();
                        const feedContainer = document.querySelector(".feed");
                        const newPostHtml = `
                            <div class="post-user">
                            </div>
                        `;
                        feedContainer.insertAdjacentHTML("afterbegin", newPostHtml);
                        postForm.reset();
                    } else {
                        console.error("Failed to submit post:", data.error);
                    }
                });
            postFormContainer.style.display = "none";
        });
    }
    function togglePostForm() {
        postFormContainer.style.display = postFormContainer.style.display === "none" ? "block" : "none";
    }

});
document.addEventListener('DOMContentLoaded', function () {
    const ratingButtons = document.querySelectorAll('.rating-button');

    ratingButtons.forEach(button => {
        button.addEventListener('click', () => {
            const postId = button.getAttribute('data-post-id');
            const rating = parseInt(button.getAttribute('data-rating'));
            console.log('Selected Rating:', rating);

            fetch(`/update_rating/?post_id=${postId}&rating=${rating}`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data && data.success) {
                        const overallRating = document.querySelector(`#overall-rating-${postId}`);
                        const total_points = data.total_points;
                        overallRating.textContent = total_points.toString();

                        console.log('Updated Rating:', total_points);
                    } else {
                        console.error('Failed to update rating');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        });
    });
});


