from flask import Blueprint, render_template, jsonify, request
from postgres_connector import fetch_all, fetch_one_column, fetch_one, update_one, update_one_column

chip_bp = Blueprint('chip', __name__)

