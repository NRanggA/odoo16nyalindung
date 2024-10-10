/** @odoo-module */

import { registry } from "@web/core/registry";
import { CharField } from "@web/views/fields/char/char_field";
import { Component, onMounted, onWillUnmount, useRef } from "@odoo/owl";

class ShowPasswordEye extends Component {
    setup(){
        // console.log(this)
    }
    // toggleShow(){
    //     console.log("togleeeee")
    //     console.log(this.hasClass("fa-eye"))
    //     // if this.
    //     // this.toggleClass('o_field_show_password fa fa-eye')
    //     // console.log(this)
    //     // console.log(this.input)
    //     // console.log(this.span)
    //     // if (this.input.el.type=='password'){
    //     //     this.input.el.type = 'text'
    //     // }
    //     // else{
    //     //     this.input.el.type = 'password'
    //     // }
    // }
} 
ShowPasswordEye.template = "ny_changespass.ShowPasswordEye"

export class ShowPassword extends CharField {
    setup(){
        super.setup()
    }
    
    toggleShow(){
        // console.log(this)
        // console.log(this.input)
        // console.log(this.span)
        if (this.input.el.type=='password'){
            this.input.el.type = 'text'
        }
        else{
            this.input.el.type = 'password'
        }
    }
}
ShowPassword.template = "ny_changespass.ShowPassword"
ShowPassword.supportedTypes = ["char"]
ShowPassword.components = {
    ShowPasswordEye,
}
registry.category("fields").add("showpassword",ShowPassword)
