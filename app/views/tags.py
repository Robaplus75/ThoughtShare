from ..extensions import db
from ..models.blog import Tags, Tagged_items, Posts

def create_tags(tags, post_id):

    for tag_name in tags:
        tag = Tags.query.filter(Tags.name==tag_name).first()
        if not tag:
            tag = Tags(name=tag_name)
            db.session.add(tag)
            db.session.commit()
            tag = Tags.query.filter(Tags.name==tag_name).first()
        

        tagged_item = Tagged_items(post_id=post_id, tag_id=tag.id)
        db.session.add(tagged_item)
    
    db.session.commit()

def update_tags(tags, post_id):
    tagged_item = Tagged_items.query.filter(Tagged_items.post_id==post_id).all()
    if tagged_item:
        for item in tagged_item:
            db.session.delete(item)
        db.session.commit()
    create_tags(tags, post_id)

def get_tags(post_id):
    post = Posts.query.filter(Posts.id==post_id).first()
    tag_ids = []
    tags = []
    for items in post.tagged_items:
        tag_ids.append(items.tag_id)
    for tag in tag_ids:
        item = Tags.query.filter(Tags.id==tag).first()
        if (item):
            tags.append(item.name)

    return tags