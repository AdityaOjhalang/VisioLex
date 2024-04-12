// Search button event listener
document.getElementById('searchButton').addEventListener('click', function() {
    var searchTerm = document.getElementById('search-query').value;
    search(searchTerm);
  });
  
  // Upload button event listener
  document.getElementById('uploadButton').addEventListener('click', function() {
    var fileInput = document.getElementById('photo-upload');
    var customLabels = document.getElementById('customLabels').value;
    uploadImage(fileInput.files[0], customLabels);
  });
  
  // Function to handle image search
  function search(searchTerm) {
    var apigClient = apigClientFactory.newClient({
      apiKey: "YOUR_API_KEY"
    });
  
    var params = {
      q: searchTerm
    };
    
    var additionalParams = {
      headers: {
        'Content-Type':"application/json"
      }
    };
  
    apigClient.searchGet(params, {}, additionalParams).then(function(res){
      console.log("Search successful:", res);
      showImages(res.data);
    }).catch(function(err){
      console.error("Search failed:", err);
    });
  }
  
  // Function to display search results
  function showImages(res) {
    var imagesContainer = document.getElementById("resultsContainer");
    imagesContainer.innerHTML = ''; // Clear existing images
  
    if (!res.length) {
      imagesContainer.innerText = "No images found.";
      return;
    }
  
    res.forEach(function(imagePath) {
      var imgElement = document.createElement("img");
      imgElement.src = imagePath; // Construct the full URL as needed
      imagesContainer.appendChild(imgElement);
    });
  }
  
  // Function to upload images
  function uploadImage(file, customLabels) {
    var apigClient = apigClientFactory.newClient({
      apiKey: "YOUR_API_KEY"
    });
  
    var reader = new FileReader();
    reader.onload = function (e) {
      var encodedImage = e.target.result;
  
      var params = {
        // Define your parameters for the PUT request
        "key": file.name,
        "bucket": "YOUR_BUCKET_NAME"
      };
  
      var additionalParams = {
        headers: {
          'Content-Type': file.type,
          'x-amz-meta-customLabels': customLabels
        }
      };
  
      apigClient.uploadBucketKeyPut(params, encodedImage, additionalParams)
        .then(function (result) {
          console.log('Image upload successful:', result);
          alert("Photo uploaded successfully.");
        }).catch(function (err) {
          console.error('Image upload failed:', err);
        });
    };
  
    reader.readAsDataURL(file);
  }
  
// document.addEventListener('DOMContentLoaded', function() {
//     const searchButton = document.getElementById('searchButton');
//     const uploadButton = document.getElementById('uploadButton');
  
//     searchButton.addEventListener('click', function() {
//       const query = document.getElementById('search-query').value;
//       searchImages(query);
//     });
  
//     uploadButton.addEventListener('click', function() {
//       const fileInput = document.getElementById('photo-upload');
//       const customLabels = document.getElementById('customLabels').value;
//       uploadImage(fileInput.files[0], customLabels);
//     });
//   });
  
//   function searchImages(query) {
//     // Implement a GET request to your backend search endpoint
//     fetch('/search?q=' + encodeURIComponent(query))
//       .then(response => response.json())
//       .then(data => {
//         displayResults(data);
//       })
//       .catch(error => console.error('Error:', error));
//   }
  
//   function uploadImage(file, labels) {
//     // Implement a PUT request to your backend upload endpoint
//     const formData = new FormData();
//     formData.append('photo', file);
  
//     const headers = new Headers({
//       'x-amz-meta-customLabels': labels
//     });
  
//     fetch('/photos', {
//       method: 'PUT',
//       headers: headers,
//       body: formData
//     })
//     .then(response => response.json())
//     .then(data => {
//       console.log('Success:', data);
//     })
//     .catch(error => console.error('Error:', error));
//   }
  
//   function displayResults(results) {
//     // Clear previous results
//     const resultsContainer = document.getElementById('resultsContainer');
//     resultsContainer.innerHTML = '';
  
//     // Add new results
//     results.forEach(result => {
//       const img = document.createElement('img');
//       img.src = result.url;
//       img.alt = result.alt;
//       img.width = 400;
//       img.height = 250;
//       resultsContainer.appendChild(img);
//     });
//   }
  