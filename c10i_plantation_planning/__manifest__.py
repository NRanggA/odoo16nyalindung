# -*- coding: utf-8 -*-
{
    "name": "Plantation Planning",
    "version": "16.0.0.1.0",
    "category": "Plantation",
    "summary": "C10I Plantation Planning",
    "description": """
        Plantation Planning
    """,
    "author": "Hendra Saputra <hendrasaputra0501@gmail.com>",
    "website": "https://www.konsalten.co.id",
    "license": "AGPL-3",
    "depends": [
        "c10i_lhm_v16",
        "ny_plantation",
        "ny_closing",
    ],
    "data": [
        "security/planning_security.xml",
        "security/ir.model.access.csv",
        
        "views/planning_crop_task_view.xml",
        "views/planning_crop_view.xml",
        
        "views/menuitems.xml",
    ],
    "installable": True
}