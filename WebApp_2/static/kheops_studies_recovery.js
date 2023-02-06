function btn_get_albums() {
	var requestURL = 'https://kheops.ehealth.hevs.ch/api/albums';
	var request = new XMLHttpRequest();
	var albumsList;

	request.open('GET', requestURL);
	request.setRequestHeader('Accept', 'application/json');
	request.setRequestHeader('Authorization', 'Bearer ' + keycloak.token);

	request.onload = function() {
		albumsList = JSON.parse(request.response);

		var albums_elmt = document.getElementById("albums");
		albums_elmt.hidden = false;

		var album_elmt = document.getElementById("get_album");
		album_elmt.hidden = false;

		var self_elmt = document.getElementById("get_albums");
		self_elmt.hidden = true;
				
		for (var i=0; i<albumsList.length ; i++){			
			newp = document.createElement ("p");
			newp.innerHTML = "<input type='radio' id='album' name ='album' value = " + albumsList[i].album_id.toString() + " > Nom de l'album : " + albumsList[i].name + "  //  nombre d'examens : " + albumsList[i].number_of_studies + "</input></br>";
			albums_elmt.insertBefore(newp, album_elmt);
		}
	};

	request.onerror = function(e){console.error(e)};
	request.send();
} 


function btn_get_studies() {
	var id_album;
	var radios = document.getElementsByName('album');
	var album_label = document.getElementById('albumID');
	var div_studies = document.getElementById('studies');
	var checkAll_elmt = document.getElementById('checkAll');
	checkAll_elmt.hidden = false;
	div_studies.hidden = false;
	
	for (var i=0; i < radios.length; i++) {
		if (radios[i].checked) {
			id_album = radios[i].value;
			console.log(id_album.toString())
			display_studies(id_album);
			album_label.value = id_album;
		}
	}
}


function btn_get_datas(){
	var chckbxs = document.getElementsByName('study');
	var studies = [];
	
	for (var i=0; i < chckbxs.length; i++) {
		var newstudy = {};
		if (chckbxs[i].checked) {
			id_study = chckbxs[i].value;
			study = (chckbxs[i].value).split(',');
			newstudy = {patient_id: study[0].toString(), study_id : study[1].toString()};
			studies.push(newstudy);

			console.log("STUDY ID : " + study[1].toString());
			console.log("PATIENT ID : " + study[0].toString());

		}
	}

	var datas = {"albumID": document.getElementById("albumID").value, "studies": studies};
	var getModels_btn = document.getElementById("get_modelsID")
	var studies_div = document.getElementById("studies")

	getModels_btn.hidden = false
	studies_div.hidden = true

	var requestURL = "http://127.0.0.1:5000/studies";
	var request = new XMLHttpRequest();

	request.open('POST', requestURL);
	request.setRequestHeader('Content-Type', 'application/json');
	request.setRequestHeader('Authorization', 'Bearer ' + keycloak.token);

	request.onload = function() {
		
	};

	request.onerror = function(e){console.error(e)};
	request.send(JSON.stringify(datas));
}


function display_studies(albumID) {
	var studiesList;
	var albumID = albumID;
	var requestURL = 'https://kheops.ehealth.hevs.ch/api/studies?album=' + albumID.toString();
	var request = new XMLHttpRequest();

	request.open('GET', requestURL);
	request.setRequestHeader('Accept', 'application/json');
	request.setRequestHeader('Authorization', 'Bearer ' + keycloak.token);

	request.onload = function() {
		
		studiesList = JSON.parse(request.response);
		var valid = document.getElementById("valide_datas_btn");
		var albums_display = document.getElementById("albums");
		albums_display.hidden = true;
		var div_studies_elmt = document.getElementById("studies");

		for (var j=0; j <studiesList.length; j++){
			
			var study_patient = studiesList[j]["00100020"].Value.toString();
			var study_id = studiesList[j]["0020000D"].Value.toString();
			var suties_list = [];
			var study = document.createElement("input");
			var newp = document.createElement("p");

			study.name = "study";
			study.type='checkbox';
			suties_list.push(study_patient)
			suties_list.push(study_id)
			study.value = suties_list;
			study_text = study_patient;			
			newp.name = study_patient;
			newp.value = study_id;
			newp.appendChild(study);
			newp.append(study_text)
			div_studies_elmt.appendChild(newp, valid);
		}
	}
	
	request.onerror = function(e){console.error(e)}
	request.send();
}
