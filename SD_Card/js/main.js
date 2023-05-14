const tabs_scroll_step = 100;
const ID_PREFIX = "event_";

const emptyData = {
    secrets: { ssid: "", password: "", timezone: "", aio_username: "", aio_key: "" },
    events: []
};

let configData = {
    secrets: { ssid: "", password: "", timezone: "", aio_username: "", aio_key: "" },
    events: []
};

let savedConfigData = {};

const event = new makeStruct("title, subtitle, forecolor, year, month, day, hour, minute, imageCountDown, imageEventDay");

// let isSwiping = false;
let tabs_container, contents_container, tabs_left_button, tabs_right_button;

/*************************************************************************/
/******************************** DIALOGS ********************************/
/*************************************************************************/
const DIALOG_OVERLAY = document.getElementById("dialog_overlay");
const DIALOG_EVENT = document.getElementById("dialog_event_edit");

const DIALOGS = [DIALOG_EVENT];

const event_id_elem = document.getElementById("dialog_event_edit_id");
const event_title_elem = document.getElementById("dialog_event_edit_title");
const event_subtitle_elem = document.getElementById("dialog_event_edit_subtitle");
const event_forecolor_elem = document.getElementById("dialog_event_edit_forecolor");
const event_year_elem = document.getElementById("dialog_event_edit_year");
const event_month_elem = document.getElementById("dialog_event_edit_month");
const event_day_elem = document.getElementById("dialog_event_edit_day");
const event_hour_elem = document.getElementById("dialog_event_edit_hour");
const event_minute_elem = document.getElementById("dialog_event_edit_minute");
const event_imageCountDown_elem = document.getElementById("dialog_event_edit_imageCountDown");
const event_imageEventDay_elem = document.getElementById("dialog_event_edit_imageEventDay");


function addEvent() {
    dialogsShowEvent(-1);
}

function areThereUnsavedChanges() {
    const retVal = !deepEqual(configData, savedConfigData);

    if (retVal) {
        console.log("There are unsaved changes");
        console.log("--- configData ---");
        console.dir(configData);
        console.log("--- savedConfigData ---");
        console.dir(savedConfigData);
    }

    return retVal;
}

// REF: https://stackoverflow.com/questions/5306680/move-an-array-element-from-one-array-position-to-another
function array_move(arr, old_index, new_index) {
    if (new_index >= arr.length) {
        var k = new_index - arr.length + 1;
        while (k--) {
            arr.push(undefined);
        }
    }
    arr.splice(new_index, 0, arr.splice(old_index, 1)[0]);
};

function deepCopy(object1) {
    if (!isObject(object1)) {
        return null;
    }

    const keys = Object.keys(object1);
    const object2 = {};

    for (const key of keys) {
        const val1 = object1[key];

        if (!isObject(val1)) {
            object2[key] = val1;
        }
        else {
            object2[key] = deepCopy(val1);
        }
    }

    return object2;
}

// REF: https://dmitripavlutin.com/how-to-compare-objects-in-javascript/
function deepEqual(object1, object2) {
    if (!isObject(object1) || !isObject(object2)) {
        return false;
    }

    const keys1 = Object.keys(object1);
    const keys2 = Object.keys(object2);

    if (keys1.length !== keys2.length) {
        return false;
    }

    for (const key of keys1) {
        const val1 = object1[key];
        const val2 = object2[key];
        const areObjects = isObject(val1) && isObject(val2);
        if (
            areObjects && !deepEqual(val1, val2) ||
            !areObjects && val1 !== val2
        ) {
            return false;
        }
    }

    return true;
}

function isValidHexColor(colorstring) {
    const VALID_HEX_CHARS = "0123456789ABCDEF";
    let isValid = true;

    if (colorstring.length == 8 && colorstring.startsWith("0x")) {
        const hexcode = colorstring.substring(2);

        for (const c in hexcode.toUpperCase()) {
            if (VALID_HEX_CHARS.indexOf(c) < 0) {
                isValid = false;
            }
        }
    }
    else {
        isValid = false;
    }

    return isValid;
}

function changeForecolor(elem) {
    const forecolorSampleDivs = document.getElementsByClassName("forecolorSample");
    const foreColor = event_forecolor_elem.value;

    let hexcode = "F0C810"; // Default forecolor

    if (isValidHexColor(foreColor)) {
        hexcode = foreColor.substring(2);
    }

    for (const item of forecolorSampleDivs) {
        item.style.backgroundColor = "#" + hexcode;
    }
}

function copyEvents() {
    const events_content = document.getElementById("eventsContent");
    const eventRows = events_content.getElementsByClassName("row");
    const EVENT_CHECKBOX_ID_PREFIX = "event_check_";

    for (let i = eventRows.length - 1; i > -1; i--) {
        if (eventRows[i].id.startsWith(ID_PREFIX)) {
            const id = eventRows[i].id.substring(ID_PREFIX.length);
            const chkbox = document.getElementById(EVENT_CHECKBOX_ID_PREFIX + id);

            if (chkbox.checked) {
                configData.events.push(deepCopy(configData.events[id]));
            }
        }
    }

    uiUpdate();
}

function deleteEvents() {
    const events_content = document.getElementById("eventsContent");
    const eventRows = events_content.getElementsByClassName("row");
    const EVENT_CHECKBOX_ID_PREFIX = "event_check_";

    for (let i = eventRows.length - 1; i > -1; i--) {
        if (eventRows[i].id.startsWith(ID_PREFIX)) {
            const id = eventRows[i].id.substring(ID_PREFIX.length);
            const chkbox = document.getElementById(EVENT_CHECKBOX_ID_PREFIX + id);

            if (chkbox.checked) {
                configData.events.splice(id, 1);
            }
        }
    }

    uiUpdate();
}

function dialogsGetMessageBox(dialogbox_element) {
    const msgBox = dialogbox_element.getElementsByClassName("message")[0];

    if (msgBox)
        msgBox.style.display = "none";

    return msgBox;
}

function dialogsHide() {
    DIALOG_OVERLAY.style.display = "none";

    for (const dialog of DIALOGS) {
        if (dialog) {
            dialog.style.display = "none";
        }
    }

    uiUpdate();
}

function dialogsShowEvent(id) {
    if (isNaN(id) || id > configData.events.length - 1) {
        return;
    }

    // get the viewport width and height  
    const viewPortWidth = window.innerWidth || self.innerWidth || parent.innerWidth || top.innerWidth;
    const viewPortHeight = window.innerHeight || self.innerHeight || parent.innerHeight || top.innerHeight;
    const title = DIALOG_EVENT.getElementsByClassName("dialog_title")[0];

    const msgBox = dialogsGetMessageBox(DIALOG_EVENT);

    if (!DIALOG_OVERLAY || !DIALOG_EVENT || !title || !event_id_elem || !event_title_elem || !event_subtitle_elem ||
        !event_forecolor_elem || !event_year_elem || !event_month_elem || !event_day_elem || !event_hour_elem ||
        !event_minute_elem || !event_imageCountDown_elem || !event_imageEventDay_elem || !msgBox) {
        console.error("ERROR: dialogsShowEvent - Failed to get required document elements")
        return;
    }

    if (id < 0) {
        const d = new Date();
        title.textContent = "Add Event";
        event_id_elem.value = "-1";
        event_title_elem.value = "";
        event_subtitle_elem.value = "";
        event_forecolor_elem.value = "0xF0C810";
        event_year_elem.value = d.getFullYear();
        event_month_elem.value = d.getMonth() + 1;
        event_day_elem.value = d.getDate();
        event_hour_elem.value = d.getHours();
        event_minute_elem.value = d.getMinutes();
        event_imageCountDown_elem.value = "";
        event_imageEventDay_elem.value = "";
    }
    else {
        title.textContent = "Edit Event";
        event_id_elem.value = id;
        event_title_elem.value = configData.events[id].title;
        event_subtitle_elem.value = configData.events[id].subtitle;
        event_forecolor_elem.value = configData.events[id].forecolor;
        event_year_elem.value = configData.events[id].year;
        event_month_elem.value = configData.events[id].month;
        event_day_elem.value = configData.events[id].day;
        event_hour_elem.value = configData.events[id].hour;
        event_minute_elem.value = configData.events[id].minute;
        event_imageCountDown_elem.value = configData.events[id].imageCountDown;
        event_imageEventDay_elem.value = configData.events[id].imageEventDay;
    }

    // Show dialog
    dialogShowEventMessage();
    DIALOG_EVENT.style.display = "block";

    // Update forecolor sample
    changeForecolor();

    // calculate the values for center alignment
    var dialogLeft = (viewPortWidth - Number(DIALOG_EVENT.offsetWidth)) / 2;
    var dialogTop = (viewPortHeight - Number(DIALOG_EVENT.offsetHeight)) / 2;

    // Show DIALOG_OVERLAY
    DIALOG_OVERLAY.style.width = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
    DIALOG_OVERLAY.style.height = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
    DIALOG_OVERLAY.style.display = "block";

    // Position dialog
    DIALOG_EVENT.style.left = dialogLeft + "px";
    DIALOG_EVENT.style.top = dialogTop + "px";
    DIALOG_EVENT.style.display = "block";
}

function dialogShowEventMessage(txtmsg) {
    const msgArea = document.getElementById("dialog_event_edit_message");

    if (!msgArea) {
        return;
    }

    if (!txtmsg || txtmsg.length == 0) {
        msgArea.textContent = "";
        msgArea.style.display = "none";
    }
    else {
        msgArea.textContent = txtmsg;
        msgArea.style.display = "block";
        console.error("ERROR: " + txtmsg);
    }
}

function edit_event(e) {
    const selectedRow = document.getElementById(ID_PREFIX + e);

    if (!selectedRow) {
        return;
    }

    if (selectedRow.classList.contains("datrowSelected")) {
        selectedRow.classList.remove("datrowSelected");
        return;
    }

    const events_content = document.getElementById("eventsContent");
    const eventRows = events_content.getElementsByClassName("row");

    // remove datrowSelected from events
    for (const itemRow of eventRows) {
        if (itemRow.id.startsWith(ID_PREFIX)) {
            itemRow.classList.remove("datrowSelected");
        }
    }

    selectedRow.classList.add("datrowSelected");

    dialogsShowEvent(e);
    event_title_elem.focus();
}

function event_save() {
    const id = event_id_elem.value;

    dialogShowEventMessage();

    if (isNaN(id) || id > configData.events.length - 1) {
        return;
    }

    // Validate that date and time are numbers and in ranges
    let isValid = true;

    let y = event_year_elem.value;
    let mo = event_month_elem.value;
    let d = event_day_elem.value;
    let h = event_hour_elem.value;
    let mi = event_minute_elem.value;

    if (isNaN(y) || isNaN(mo) || isNaN(d) || isNaN(h) || isNaN(mi)) {
        dialogShowEventMessage("Date and Time must be numeric values!");
        return;
    }
    else if (y < 1970 || y > 3000 || mo < 1 || mo > 12 || d < 1 || d > 31 || h < 0 || h > 23 || mi < 0 || mi > 59) {
        dialogShowEventMessage("Date and Time must be within range values!");
        return;
    }
    else if (!isValidDate(y, mo, d, h, mi)) {
        dialogShowEventMessage("Date and Time must a valid date!");
        return;
    }
    else if (!isValidHexColor(event_forecolor_elem.value)) {
        dialogShowEventMessage("Forecolor is not a valid color! Enter in the format of 0xRRGGBB, where RR GG BB are 00 through FF");
        return;
    }



    // Standardize hour and minute to two characters
    // Not certain if this is necessary
    if (event_hour_elem.value.length == 1) {
        event_hour_elem.value = "0" + event_hour_elem.value;
    }
    if (event_minute_elem.value.length == 1) {
        event_minute_elem.value = "0" + event_minute_elem.value;
    }

    let hide_dialog = false;

    if (event_id_elem.value < 0) {   // Add new
        configData.events.push({
            title: event_title_elem.value,
            subtitle: event_subtitle_elem.value,
            forecolor: event_forecolor_elem.value,
            year: event_year_elem.value,
            month: event_month_elem.value,
            day: event_day_elem.value,
            hour: event_hour_elem.value,
            minute: event_minute_elem.value,
            imageCountDown: event_imageCountDown_elem.value,
            imageEventDay: event_imageEventDay_elem.value
        });
        hide_dialog = true;
    }
    else {  // Edit
        //Object.assign({}, configData.events, { timespan: action.timespan.value, customTimespan: action.timespan.value})
        configData.events[id] = {
            ...configData.events[id],
            title: event_title_elem.value,
            subtitle: event_subtitle_elem.value,
            forecolor: event_forecolor_elem.value,
            year: event_year_elem.value,
            month: event_month_elem.value,
            day: event_day_elem.value,
            hour: event_hour_elem.value,
            minute: event_minute_elem.value,
            imageCountDown: event_imageCountDown_elem.value,
            imageEventDay: event_imageEventDay_elem.value
        };
        hide_dialog = true;
    }

    if (hide_dialog) {
        dialogsHide();
        uiUpdate();
    }
}

// https://www.w3schools.com/html/tryit.asp?filename=tryhtml5_draganddrop

function eventAllowDrop(e) {
    e.preventDefault();
}

function eventDrag(e) {
    e.dataTransfer.setData("target_id", e.target.id);
}

function eventDrop(e) {
    e.preventDefault();
    e.stopPropagation();

    const data = e.dataTransfer.getData("target_id");   // Moved
    const target_li_id = e.target.closest("div").id;    // Dropped To
    if (data && target_li_id) {
        if (!data.startsWith(ID_PREFIX) || !target_li_id.startsWith(ID_PREFIX)) {
            return;
        }
        const fromIndex = data.substring(ID_PREFIX.length);
        const toIndex = target_li_id.substring(ID_PREFIX.length);

        if (isNaN(fromIndex) || isNaN(toIndex) || fromIndex == toIndex) {
            return;
        }

        array_move(configData.events, fromIndex, toIndex);

        uiUpdate();
    }
}

function getClosestElem(currentElement, selector) {
    let returnElement

    while (currentElement.parentNode && !returnElement) {
        currentElement = currentElement.parentNode
        returnElement = currentElement.querySelector(selector)
    }

    return returnElement
}

function getTabContainer(tabId) {
    let containerId = null;
    let tab = document.getElementById(tabId);

    if (tab && tab.id && tab.id.endsWith("Tab")) {
        let containerId_temp = tab.id.substring(0, tabId.length - 3) + "Content";

        if (document.getElementById(containerId_temp)) {
            containerId = containerId_temp;
        }
    }

    return containerId;
}

function init() {
    savedConfigData = deepCopy(configData);

    tabs_container = document.getElementById("tabs");
    contents_container = document.getElementById("contents");
    tabs_left_button = document.getElementById("lefttab");
    tabs_right_button = document.getElementById("righttab");

    if (tabs_container) {
        for (const item of tabs_container.getElementsByTagName("li")) {
            if (item.id && item.id.length > 0 && item.id.endsWith("Tab")) {
                if (getTabContainer(item.id)) {
                    item.addEventListener("click", showTab);
                }
            }
        }
    }

    // Show the first tab/file tab
    if (tabs_container.getElementsByTagName("li") && tabs_container.getElementsByTagName("li").length > 0) {
        tabs_container.getElementsByTagName("li")[0].click();
    }

    // Add event listerns to the left tab and right tab buttons
    if (tabs_left_button) {
        tabs_left_button.addEventListener("click", function () {
            const step_size = tabs_scroll_step <= tabs_container.parentElement.offsetWidth ? tabs_scroll_step : tabs_container.parentElement.offsetWidth;
            tabs_container.parentElement.scrollLeft -= step_size;
            tabsUpdateScrollButtonsDisabledState();
        });
    }

    if (tabs_right_button) {
        tabs_right_button.addEventListener("click", function () {
            const step_size = tabs_scroll_step <= tabs_container.parentElement.offsetWidth ? tabs_scroll_step : tabs_container.parentElement.offsetWidth;
            tabs_container.parentElement.scrollLeft += step_size;
            tabsUpdateScrollButtonsDisabledState();
        });
    }

    tabsUpdateScrollButtonsDisabledState();
    uiUpdate();
}

function isObject(object) {
    return object != null && typeof object === 'object';
}

function isValidDate(y, mo, d, h, mi) {
    const dateString = y + "-" + mo + "-" + d + " " + h + ":" + mi;

    const dte = new Date();
    const timestamp = Date.parse(dateString);
    dte.setTime(timestamp);
    if (isNaN(timestamp)) {
        return false;
    }
    else if (dte.getFullYear() != y || dte.getMonth() + 1 != mo || dte.getDate() != d || dte.getHours() != h || dte.getMinutes() != mi) {
        return false;
    }

    return true;
}

function loadFile() {
    if (areThereUnsavedChanges()) {
        if (confirm("Changes you made may not be saved.") == false) {
            return;
        }
    }

    const inputFile = document.createElement('input');
    inputFile.type = "file";
    inputFile.addEventListener("change", function (e) {
        const file = e.target.files[0];
        if (!file) {
            return;
        }
        const reader = new FileReader();

        configData = deepCopy(emptyData);

        reader.onload = function (e) {
            const contents = e.target.result;
            const data = JSON.parse(contents);

            for (const key of Object.keys(data)) {
                configData[key] = data[key];
            }

            savedConfigData = deepCopy(configData);

            uiUpdate();
        };
        reader.readAsText(file);
    });
    inputFile.click();
}

/**
 * @constructor Generates a constructor for a given data structure
 * @param {string} keys separated by a comma + whitespace. struct('id, name, age')
 * @returns {constructor} Constructor for the new struct
 */
function makeStruct(keys) {
    if (!keys) return null;
    const k = keys.split(', ');
    const count = k.length;

    /** @constructor */
    function constructor() {
        for (let i = 0; i < count; i++) this[k[i]] = arguments[i];
    }
    return constructor;
}

function saveFile() {
    const localStorageCopy = JSON.stringify(configData);
    const a = document.createElement('a');
    const file = new Blob([localStorageCopy], { type: "text/plain" });

    a.href = URL.createObjectURL(file);
    a.download = "config.json";
    a.click();
    URL.revokeObjectURL(a.href);

    savedConfigData = deepCopy(configData);
}

function selectEvents(elem) {
    const checkItems = elem.checked;
    const events_content = document.getElementById("eventsContent");
    const eventRows = events_content.getElementsByClassName("row");
    const EVENT_CHECKBOX_ID_PREFIX = "event_check_";

    for (const item of eventRows) {
        if (item.id.startsWith(ID_PREFIX)) {
            const id = item.id.substring(ID_PREFIX.length);
            const chkbox = document.getElementById(EVENT_CHECKBOX_ID_PREFIX + id);

            chkbox.checked = checkItems;
        }
    }

    uiUpdateDelete();
}

function showPassword(e) {
    const pswdInput = getClosestElem(e, "input");

    if (pswdInput) {
        if (pswdInput.type === "password") {
            pswdInput.type = "text";
            e.value = "Hide";
        } else {
            pswdInput.type = "password";
            e.value = "Show";
        }
    }
}

function showTab() {
    let containerId = getTabContainer(this.id);

    // Set all tabs to default and change current
    if (tabs_container) {
        for (const item of tabs_container.getElementsByTagName("li")) {
            if (item.id && item.id.length > 0 && item.id.endsWith("Tab")) {
                item.classList.remove("selected");

                if (item.id == this.id) {
                    item.classList.add("selected");

                    // Make the selected tab fully visible if part of it is hidden
                    if (item.offsetLeft < (tabs_container.parentElement.offsetLeft + tabs_container.parentElement.scrollLeft)) {
                        tabs_container.parentElement.scrollLeft -= tabs_scroll_step;
                        tabsUpdateScrollButtonsDisabledState();
                    }
                    else if ((item.offsetLeft + item.offsetWidth) > (tabs_container.parentElement.offsetLeft + tabs_container.parentElement.scrollLeft + tabs_container.parentElement.offsetWidth)) {
                        tabs_container.parentElement.scrollLeft += tabs_scroll_step;
                        tabsUpdateScrollButtonsDisabledState();
                    }

                }
            }
        }
    }

    // Hide all content and display selected content
    if (contents_container) {
        for (const item of contents_container.getElementsByTagName("div")) {
            if (item.id && item.id.length > 0 && item.id.endsWith("Content")) {
                item.style.display = "none";
            }

            if (containerId && containerId == item.id) {
                item.style.display = "initial";
            }
        }
    }
}

function tabsUpdateScrollButtonsDisabledState() {
    tabs_left_button.disabled = false;
    tabs_right_button.disabled = false;

    if (tabs_container.parentElement.scrollLeft == 0) {
        tabs_left_button.disabled = true;
    }
    if (tabs_container.parentElement.offsetWidth + tabs_container.parentElement.scrollLeft >= tabs_container.parentElement.scrollWidth) {
        tabs_right_button.disabled = true;
    }
}

function uiUpdate() {
    const ssidField = document.getElementById("ssid");
    const passwordField = document.getElementById("password");
    const timezoneField = document.getElementById("timezone");
    const aioUsernameField = document.getElementById("aio_username");
    const aioKeyField = document.getElementById("aio_key");
    const checkboxAll = document.getElementById("selectAllCheckbox");

    if (ssidField) {
        ssidField.value = configData.secrets.ssid;
    }
    if (passwordField) {
        passwordField.value = configData.secrets.password;
    }
    if (timezoneField) {
        timezoneField.value = configData.secrets.timezone;
    }
    if (aioUsernameField) {
        aioUsernameField.value = configData.secrets.aio_username;
    }
    if (aioKeyField) {
        aioKeyField.value = configData.secrets.aio_key;
    }

    const events_content = document.getElementById("eventsContent");
    const events_none_div = document.getElementById("events_none");
    const events_header_row = document.getElementById("events_header");
    let existingNode = document.getElementById("events_header");

    const eventRows = events_content.getElementsByClassName("row");

    // remove any existing events
    for (let i = eventRows.length - 1; i > -1; i--) {
        if (eventRows[i].id.startsWith(ID_PREFIX)) {
            eventRows[i].remove();
        }
    }

    if (configData.events.length == 0) {
        events_none_div.style.display = "initial";
        events_header_row.style.display = "none";
        checkboxAll.disabled = true;
    }
    else {
        events_none_div.style.display = "none";
        events_header_row.style.display = "table-row";
        checkboxAll.disabled = false;

        for (let i = 0; i < configData.events.length; i++) {
            /*
            const rowDiv = document.createElement("div", { class: "row", id: ID_PREFIX + i });
            const check = document.createElement("input", { type: "checkbox", id: "event_check_" + i })
            const idSpan = document.createElement("span", { id: "event_id_" + i, textContent: i });
            const titleSpan = document.createElement("span", { id: "event_title_" + i, textContent: configData.events[i].title });
            const subtitleSpan = document.createElement("span", { id: "event_subtitle_" + i, textContent: configData.events[i].subtitle });
            const forecolorSpan = document.createElement("span", { id: "event_forecolor_" + i, textContent: configData.events[i].forecolor });
            const yearSpan = document.createElement("span", { id: "event_year_" + i, textContent: configData.events[i].year });
            const monthSpan = document.createElement("span", { id: "event_month_" + i, textContent: configData.events[i].month });
            const daySpan = document.createElement("span", { id: "event_day_" + i, textContent: configData.events[i].day });
            const hourSpan = document.createElement("span", { id: "event_hour_" + i, textContent: configData.events[i].hour });
            const minuteSpan = document.createElement("span", { id: "event_minute_" + i, textContent: configData.events[i].minute });
            const imageCountDownSpan = document.createElement("span", { id: "event_imageCountDown_" + i, textContent: configData.events[i].imageCountDown });
            const imageEventDaySpan = document.createElement("span", { id: "event_imageEventDay_" + i, textContent: configData.events[i].imageEventDay });
            */

            const rowDiv = document.createElement("div");
            rowDiv.id = ID_PREFIX + i;
            rowDiv.classList.add("row", "datarow");
            rowDiv.draggable = true;
            rowDiv.addEventListener("mousedown", function (e) {
                const eTagName = e.target.tagName.toUpperCase();
                if (eTagName == "INPUT" || eTagName == "SELECT" || eTagName == "BUTTON" || eTagName == "TEXTAREA" || eTagName == "A" || eTagName == "LABEL")
                    return;
                myDragMove.startMoving(this, "dialog_overlay", e);
            });
            rowDiv.addEventListener("mouseup", function (e) {
                myDragMove.stopMoving("dialog_overlay");
            });
            rowDiv.addEventListener("dragstart", eventDrag);
            rowDiv.addEventListener("drop", eventDrop);
            rowDiv.addEventListener("dragover", eventAllowDrop);
            // Edit Row
            rowDiv.addEventListener("click", function (event) {
                edit_event(i);
            });
            rowDiv.addEventListener("mouseover", function (event) {
                rowDiv.classList.add("datarowhover");
            });
            rowDiv.addEventListener("mouseout", function (event) {
                rowDiv.classList.remove("datarowhover");
            });
            // Make accessible
            rowDiv.ariaRoleDescription = "";
            rowDiv.role = "button";
            rowDiv.addEventListener("keydown", (event) => {
                if (event.key == "Enter") {
                    edit_event(i);
                }
                else if (event.key == "ArrowUp") {
                    const fromIndex = i;
                    const toIndex = i - 1;

                    if (isNaN(fromIndex) || isNaN(toIndex) || fromIndex == toIndex) {
                        return;
                    }

                    array_move(configData.events, fromIndex, toIndex);

                    uiUpdate();
                }
                else if (event.key == "ArrowDown") {
                    const fromIndex = i;
                    const toIndex = i + 1;

                    if (isNaN(fromIndex) || isNaN(toIndex) || fromIndex == toIndex) {
                        return;
                    }

                    array_move(configData.events, fromIndex, toIndex);

                    uiUpdate();
                }
                else {
                    console.log("Key pressed -> " + event.key);
                }
            });


            const check = document.createElement("span");
            check.classList.add("datacell");
            check.classList.add("datacellcheck");
            const checkbox = document.createElement("input")
            checkbox.id = "event_check_" + i;
            checkbox.type = "checkbox";
            //checkbox.classList.add("datacell");
            checkbox.addEventListener("click", function (event) {
                event.stopPropagation();

                uiUpdateDelete();
            });
            check.appendChild(checkbox);

            const idSpan = document.createElement("span");
            idSpan.id = "event_id_" + i;
            idSpan.textContent = i;
            idSpan.classList.add("datacell");
            const titleSpan = document.createElement("span");
            titleSpan.id = "event_title_" + i;
            titleSpan.textContent = configData.events[i].title;
            titleSpan.classList.add("datacell");
            const subtitleSpan = document.createElement("span", { id: "event_subtitle_" + i, textContent: configData.events[i].subtitle });
            subtitleSpan.id = "event_subtitle_" + i;
            subtitleSpan.textContent = configData.events[i].subtitle;
            subtitleSpan.classList.add("datacell");
            const forecolorSpan = document.createElement("span", { id: "event_forecolor_" + i, textContent: configData.events[i].forecolor });
            forecolorSpan.id = "event_forecolor_" + i;
            forecolorSpan.textContent = configData.events[i].forecolor;
            forecolorSpan.classList.add("datacell");
            const yearSpan = document.createElement("span", { id: "event_year_" + i, textContent: configData.events[i].year });
            yearSpan.id = "event_year_" + i;
            yearSpan.textContent = configData.events[i].year;
            yearSpan.classList.add("datacell");
            const monthSpan = document.createElement("span", { id: "event_month_" + i, textContent: configData.events[i].month });
            monthSpan.id = "event_month_" + i;
            monthSpan.textContent = configData.events[i].month;
            monthSpan.classList.add("datacell");
            const daySpan = document.createElement("span", { id: "event_day_" + i, textContent: configData.events[i].day });
            daySpan.id = "event_day_" + i;
            daySpan.textContent = configData.events[i].day;
            daySpan.classList.add("datacell");
            const hourSpan = document.createElement("span", { id: "event_hour_" + i, textContent: configData.events[i].hour });
            hourSpan.id = "event_hour_" + i;
            hourSpan.textContent = configData.events[i].hour;
            hourSpan.classList.add("datacell");
            const minuteSpan = document.createElement("span", { id: "event_minute_" + i, textContent: configData.events[i].minute });
            minuteSpan.id = "event_minute_" + i;
            minuteSpan.textContent = configData.events[i].minute;
            minuteSpan.classList.add("datacell");
            const imageCountDownSpan = document.createElement("span", { id: "event_imageCountDown_" + i, textContent: configData.events[i].imageCountDown });
            imageCountDownSpan.id = "event_imageCountDown_" + i;
            imageCountDownSpan.textContent = configData.events[i].imageCountDown;
            imageCountDownSpan.classList.add("datacell");
            const imageEventDaySpan = document.createElement("span", { id: "event_imageEventDay_" + i, textContent: configData.events[i].imageEventDay });
            imageEventDaySpan.id = "event_imageEventDay_" + i;
            imageEventDaySpan.textContent = configData.events[i].imageEventDay;
            imageEventDaySpan.classList.add("datacell");

            rowDiv.appendChild(check);
            //rowDiv.appendChild(idSpan);
            rowDiv.appendChild(titleSpan);
            rowDiv.appendChild(subtitleSpan);
            rowDiv.appendChild(forecolorSpan);
            rowDiv.appendChild(yearSpan);
            rowDiv.appendChild(monthSpan);
            rowDiv.appendChild(daySpan);
            rowDiv.appendChild(hourSpan);
            rowDiv.appendChild(minuteSpan);
            rowDiv.appendChild(imageCountDownSpan);
            rowDiv.appendChild(imageEventDaySpan);

            //insertAfter(rowDiv, existingNode);
            existingNode.after(rowDiv);

            existingNode = document.getElementById(rowDiv.id);
        }
    }

    uiUpdateDelete();
}

function uiUpdateDelete() {
    const deleteButton = document.getElementById("deleteSelectedButton");
    const copyButton = document.getElementById("copySelectedButton");
    const events_content = document.getElementById("eventsContent");
    const eventRows = events_content.getElementsByClassName("row");
    const EVENT_CHECKBOX_ID_PREFIX = "event_check_";

    let itemsChecked = 0;

    // Are any checkboxes checked?
    for (const item of eventRows) {
        if (item.id.startsWith(ID_PREFIX)) {
            const id = item.id.substring(ID_PREFIX.length);
            const chkbox = document.getElementById(EVENT_CHECKBOX_ID_PREFIX + id);

            if (chkbox) {
                if (chkbox.checked) {
                    itemsChecked++;
                }
            }
        }
    }

    deleteButton.disabled = true;
    copyButton.disabled = true;
    if (itemsChecked > 0) {
        deleteButton.disabled = false;
        copyButton.disabled = false;
    }
}

function updateData(e) {
    if (!e.id || e.id.length <= 0) {
        return;
    }

    switch (e.id) {
        case ("ssid"):
            configData.secrets.ssid = e.value;
            break;
        case ("password"):
            configData.secrets.password = e.value;
            break;
        case ("timezone"):
            configData.secrets.timezone = e.value;
            break;
        case ("aio_username"):
            configData.secrets.aio_username = e.value;
            break;
        case ("aio_key"):
            configData.secrets.aio_key = e.value;
            break;
        default:
            break;
    }
}

init()

window.addEventListener("resize", tabsUpdateScrollButtonsDisabledState);

window.addEventListener('beforeunload', function (e) {
    if (areThereUnsavedChanges()) {
        e.preventDefault();
        e.returnValue = '';
        return;
    }

    delete e['returnValue'];
});

for (const button of document.getElementsByClassName("button_cancel")) {
    button.addEventListener("click", dialogsHide);
}