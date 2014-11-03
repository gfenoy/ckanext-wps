// The "Use" button
// WPS preview module
this.ckan.module('wpspreview', function (jQuery, _) {
    // Private
    var defaultVersion = "1.1.1";
    var preferredFormat = "image/png";
    var proxy = false;
    return {
	options: {
	    i18n: {
	    }
	},
	initialize: function () {
	    var closure=this;
	    jQuery.proxyAll(this, /_on/);
	    this.el.find("a").each(function(index){
		if(index==0){
		    $(this).click(function(e){e.preventDefault();closure.loadDescription(closure,e,this)});
		}
		else{
		    $(this).click(function(e){e.preventDefault();closure.loadExecution(closure,e,this)});
		}
	    });
	    this.el.ready(this._onReady);
	},
	_onReady: function() {
	},
	_snippetReceived: false,
	loadExecution: function() {
	    arguments[1].preventDefault();
	    var closure=arguments[0];
	    $(".resource-list").find("p.full_description").each(function(){
		$(this).html("");
	    });
	    if (!closure._snippetReceived) {
		closure.turl=$(arguments[2]).attr("href");
		jQuery.ajax({
		    method: 'get',
		    url: $(arguments[2]).attr("href"),
		    success: function (results){
			closure._onReceiveSnippet(results);
			//Load new data-module
			try{
			    var tmp=["wpsdsl","wpsfl","wpsesb"];
			    for(var j=0;j<tmp.length;j++){
				var list=jQuery('[data-module="'+tmp[j]+'"]');
				for(i=0;i<list.length;i++)
				    ckan.module.initializeElement(list[i])
			    }
			}catch(e){}
		    },
		    error: function () {
			console.log("Failed to load snippets");
		    }
		});
		/*closure.el.parent().parent().find("p.full_description").each(function(){
		    $(this).load(closure.turl+" body");
		});*/
	    }
	},
	loadDescription: function() {
	    arguments[1].preventDefault();
	    var closure=arguments[0];
	    $(".resource-list").find("p.full_description").each(function(){
		$(this).html("");
	    });
	    if (!closure._snippetReceived) {
		closure.turl=$(arguments[2]).attr("href");
		jQuery.ajax({
		    method: 'get',
		    url: $(arguments[2]).attr("href"),
		    success: function (results){
			closure._onReceiveSnippet(results);
		    },
		    error: function () {
			console.log("Failed to load snippets");
		    }
		});
	    }
	},
	_onReceiveSnippet: function(html) {
	    var closure=this;
	    this.el.parent().parent().find("p.full_description").each(function(){
		var node=$(html).filter('#pDescription');
		$(this).html(node);
	    });
	},
	execute: function() {
	    var closure=arguments[0];
	    console.log("execute called ! "+closure.el.attr("data-wpsid"));
	}
    }
});

// The Datasets list
// WPSDSL 
this.ckan.module('wpsdsl', function (jQuery, _) {
    return {
	options: {
	    i18n: {
	    }
	},
	hasResources: false,
	loadResources: function(){
	    var closure=this;
	    var format=closure.el.attr("data-format");
	    var sformat=closure.el.attr("data-format").split("/")[1];
	    for(i=0;i<closure.resources.length;i++){
		//console.log(closure.resources[i]);
		var lf=closure.resources[i]["mimetype"];
		var lsf=null;
		if(lf)
		    lsf=lf.split("/")[1];
		console.log(lf);
		console.log(lsf);
		/*var lsf=results["result"]["resources"][i]["mimetype"].split("/")[1];*/
		if(lf==format || lsf==sformat)
		    $("#"+closure.el.attr("data-target")).append('<option value="'+closure.resources[i]["id"]+'">'+closure.resources[i]["name"]+'</option>');
	    }

	},
	initialize: function () {
	    var closure=this;
	    jQuery.proxyAll(this, /_on/);
	    console.log("Initialize wpsdsl !");
	    this.el.change(function(){
		closure._onChange(this);
	    });
	    this.el.ready(this._onReady);
	},
	_onChange: function(el){
	    var closure=this;
	    console.log($(el).val());
	    $("#"+closure.el.attr("data-target")).html('<option value="-1">'+"First select a dataset"+'</option>');
	    if($(el).val()!="-1"){
		if(!closure.hasResources)
		    jQuery.ajax({
			method: 'get',
			url: "/api/3/action/package_show?id="+$(el).val(),
			success: function (results){
			    closure.hasResources=true;
			    console.log("execute called ! "+closure.el.attr("data-target"));
			    console.log(results);
			    closure.resources=results["result"]["resources"];
			    closure.loadResources();
			},
			error: function () {
			    console.log("Failed to load snippets");
			}
		    });
		else
		    closure.loadResources();
	    }
	}
    }
});

// The Formats list
// WPSFL WPS formats list
this.ckan.module('wpsfl', function (jQuery, _) {
    return {
	filters:{
	    "application/json": "application/javascript"
	},
	options: {
	    i18n: {
	    }
	},
	initialize: function () {
	    var closure=this;
	    jQuery.proxyAll(this, /_on/);
	    console.log("Initialize wpsfl !");
	    closure.el.change(function(){
		console.log($(this).val());
		console.log("FILTERS: "+closure.filters[$(this).val()]);
		if(closure.filters[$(this).val()])
		    $("#"+closure.el.attr("data-target")).attr("data-format",closure.filters[$(this).val()]);
		else
		    $("#"+closure.el.attr("data-target")).attr("data-format",$(this).val());
		var prev=$("#"+closure.el.attr("data-target")).val();
		$("#"+closure.el.attr("data-target")).val(prev).change();
		console.log(prev);
	    });
	    this.el.ready(this._onReady);
	}
    }
});

// The WPS Execute button
// WPSESB WPS formats list
this.ckan.module('wpsesb', function (jQuery, _) {
    return {
	options: {
	    i18n: {
	    }
	},
	initialize: function () {
	    var closure=this;
	    jQuery.proxyAll(this, /_on/);
	    console.log("Initialize wpsesb !");
	    closure.el.click(function(){
		var tmp=$("#"+closure.el.attr("data-target-form")).serializeArray();
		var data={};
		for(var i=0;i<tmp.length;i++){
		    data[tmp[i].name]=tmp[i].value;
		}
		$.ajax({
		    url: "/api/3/action/ckanext_wps_execute",
		    //type: 'POST',
		    //dataType: 'jsonp',
		    data: $("#"+closure.el.attr("data-target-form")).serialize(),
		    success: function(data) {
			console.log('Execution ok')
		    }
		});
	    });
	    this.el.ready(this._onReady);
	}
    }
});
